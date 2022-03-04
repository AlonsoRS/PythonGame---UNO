import socket
import SocketsCodigos
import FunctionsFinal
import threading
import pickle
import json
import time
from Objetos import Tarjeta
import Archivos

Jugadores = []
JugadoresObjetos = []
NombreServidor = socket.gethostname()
IP = socket.gethostbyname(NombreServidor)
Puerto = 5050
Formato = "utf-8"

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind((socket.gethostname(), Puerto)) # Servidor Local
#servidor.bind(("", Puerto))  # Servidor Nube
servidor.listen(2)

# Juego
MazoPrincipal = []
CartaEnMesa = []
idJugadorTurnoActual = 0
seGano = False

def IniciarJuego():
    global MazoPrincipal, CartaEnMesa
    print("-------Inicio del Juego-------")
    MazoPrincipal = FunctionsFinal.CrearMazo()
    FunctionsFinal.SuffleMazo(MazoPrincipal)
    CartasXJugador = FunctionsFinal.RepartirCartar(MazoPrincipal, 2)
    CartaEnMesa = FunctionsFinal.ConseguirCartaEnMesa(MazoPrincipal)
    [print(f"Jugador {i+1}: {CartasXJugador[i]}") for i in range(len(CartasXJugador))]
    print(f"Carta en mesa: {CartaEnMesa}")

    Mensajes = []
    for CartasJugador in CartasXJugador:
        Cartas = [Tarjeta.convertirTarjetaADict(carta) for carta in CartasJugador]
        Mensajes.append(FormatearMensaje(SocketsCodigos.RecivirCartas, json.dumps(Cartas)))
        #print(f"Cartas Jugador {Cartas}")
    #print(f"Carta en mesa: {CartaEnMesa}")
    EscribirAClientes(Mensajes, False)  # Enviar Cartas
    time.sleep(0.25)
    EscribirAClientes(FormatearMensaje(SocketsCodigos.CartaEnMesa, CartaEnMesa), True)  # Enviar carta en Mesa
    time.sleep(0.25)
    EscribirAJugador(idJugadorTurnoActual, FormatearMensaje(SocketsCodigos.InidicarTurnoActual,""))
    #Indica al jugador #1 que es su turno


def FormatearMensaje(comando, mensaje=""):
    return f"{str(comando)};{str(mensaje)}"


def EscribirAJugador(idJugador,mensaje):
    JugadoresObjetos[idJugador].send(mensaje.encode(Formato))


def EscribirATodosMenosActual(actual, mensaje):
    for i in range(len(JugadoresObjetos)):
        if i != actual:
            JugadoresObjetos[i].send(mensaje.encode(Formato))


def EscribirAClientes(Mensajes, mismoMensaje):
    for i in range(len(JugadoresObjetos)):
        if mismoMensaje:
            JugadoresObjetos[i].send(Mensajes.encode(Formato))
        else:
            JugadoresObjetos[i].send(Mensajes[i].encode(Formato))


def ControladorCliente(conn, addr):
    global CartaEnMesa,seGano
    print(f"El cliente con IP: {addr} se ha conectado.\n")
    connectado = True
    idJugador = threading.active_count()-2
    nombreJugador = ""

    if threading.active_count()-1 > 2: # Validar espacio en el servidor (Servidor lleno)
        conn.send(FormatearMensaje(SocketsCodigos.SolicitudDenegada, "Disculpe ya esta completo la partida").encode(Formato))
        print(f"Se ha rechazado al jugador {idJugador} debido a que la sala ya esta llena.")
        print(f"El cliente : {addr} se ha desconnectado.")
        conn.close
        connectado = False
        return

    JugadoresObjetos.append(conn)
    while connectado:
        msg = conn.recv(1024).decode(Formato)
        print(f"Mensaje recivido: {str(msg)}")
        MSG = msg.split(";")

        if MSG[0] == SocketsCodigos.AgregarUsuario:
            nombreJugador = str(MSG[1])
            Jugadores.append(nombreJugador)
            conn.send(f"Hola  {nombreJugador}".encode(Formato))
            print(f"Jugadores connectados: {Jugadores}")
            if threading.active_count()-1 == 2:  # Empezar juego porque ya hay dos jugadores
                EscribirAClientes(FormatearMensaje(SocketsCodigos.EnviarJugadores,json.dumps(Jugadores)), True)
                time.sleep(1)
                IniciarJuego()
        elif MSG[0] == SocketsCodigos.MandarCartaServidor:
            CartaEnMesa = Tarjeta.convertirTarjetaAObjeto(json.loads(MSG[1]))
            MazoPrincipal.append(CartaEnMesa)  # Se agrega carta al final
            EscribirAClientes(FormatearMensaje(SocketsCodigos.CartaEnMesa, CartaEnMesa), True)
            if not seGano:
                EscribirATodosMenosActual(idJugador, FormatearMensaje(SocketsCodigos.InidicarTurnoActual, ""))
                time.sleep(0.5)
        elif MSG[0] == SocketsCodigos.PedirCarta:
            CartaAMandar = FunctionsFinal.ConseguirCartaEnMesa(MazoPrincipal)  # Se usa la misma funcion ya q retorna una sola carta
            #CartaDict = Tarjeta.convertirTarjetaADict(CartaAMandar)
            EscribirAJugador(idJugador, FormatearMensaje(SocketsCodigos.RecivirCarta, CartaAMandar))

        elif MSG[0] == SocketsCodigos.SaltarTurno:
            EscribirATodosMenosActual(idJugador, FormatearMensaje(SocketsCodigos.InidicarTurnoActual, ""))
            time.sleep(0.5)

        elif MSG[0] == SocketsCodigos.MensajeJugadorGanador:
            seGano = False
            EscribirATodosMenosActual(idJugador, FormatearMensaje(SocketsCodigos.MensajeJugadorPerdedor, ""))
            Archivos.Verificar(Jugadores[0], Jugadores[1], Jugadores[idJugador])

        elif MSG[0] == SocketsCodigos.DESCONECTAR:
            print(f"El cliente : {nombreJugador} se ha desconnectado.")
            JugadoresObjetos.pop(idJugador)
            Jugadores.pop(idJugador)
            connectado = False

    conn.close()


def IniciarServidor():
    servidor.listen()
    while True:
        conn, addr = servidor.accept()
        hilo = threading.Thread(target=ControladorCliente, args=(conn, addr))
        hilo.start()
        print(f"Numero de clientes connectados: {threading.activeCount()-1}")

print("Se ha iniciado el servidor de UNO")
print(f"Servidor: {NombreServidor} IP: {IP}")
print(f"Puerto: {Puerto}")
print()
IniciarServidor()
