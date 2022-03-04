import pygame, sys, os
from pygame.locals import *
import Colores as Cl
import threading
from Objetos import Tarjeta
import socket, SocketsCodigos
import json
import FunctionsFinal

# Variables Principales
pantallaActual = "Inicio"
tarjetas = []
tarjetaMesa = None
tarjetaActual, cantidadDeTarjetas = 0, 0
Jugador, Rival = "Jugador 1", "Rival"
Cerrar = False
MiTurno, MostrarPedirCarta, SePidioCarta, MostrarSaltarTurno = False, False, False, False
SeGano = False
TerminoJuego = False

# Variables Sockets:
ContinuarHilo = False
socketCliente = None
NombreServidor, IP, Puerto = "", "", 5050
Formato = "utf-8"

# Variables Pygame
pygame.font.init()
ResW, ResH = 1280, 720
fondoInicio = pygame.image.load("Imagenes/pantallaInicial.png")  # Fondo de Juego
fondoGanador = pygame.image.load("Imagenes/fondoGanador.jpeg")  # Fondo de Ganador
fondoPerdedor = pygame.image.load("Imagenes/fondoPerdedor.jpeg")  # Fondo de Perdedor
fondoJuego = pygame.image.load("Imagenes/PANTALLA DE JUEGO 2.png")  # Fondo de Juego
# tarjetaPrueba = pygame.image.load("Imagenes/Cartas/9Azul.jpeg")  # CARGA DE IMAGENES
# tarjetaPedirCarta = pygame.image.load("Imagenes/Cartas/8Verde.jpeg")
myfont = pygame.font.SysFont('Comic Sans MS', 40)
myfont2 = pygame.font.SysFont('Comic Sans MS', 20)
textSurJugador = myfont.render(Jugador, False, Cl.BlANCO)
textSurRival = myfont.render(Rival, False, Cl.BlANCO)


def Connectar(ConnectarANube):
    if ConnectarANube:
        nombreServidor = "Linode Server"
        ip = "192.81.135.124"
    else:
        nombreServidor = socket.gethostname()
        ip = socket.gethostbyname(nombreServidor)
    return ip, Puerto


def CerrarConneccion():
    global ContinuarHilo
    ContinuarHilo = False
    EnviarMensaje(SocketsCodigos.DESCONECTAR)


def EnviarMensaje(comando, mensaje=""):
    if ContinuarHilo:
        socketCliente.send(str(f"{comando};{mensaje}").encode(Formato))
    else:
        print("No se ha enviado el mensaje")


def Listener():
    global Cerrar
    global pantallaActual
    global Rival
    global textSurJugador
    global textSurRival
    global cantidadDeTarjetas
    global tarjetaMesa
    global MiTurno
    global SePidioCarta, MostrarSaltarTurno, MostrarPedirCarta
    global SeGano,TerminoJuego

    while ContinuarHilo and not Cerrar:
        msg = socketCliente.recv(1024).decode(Formato)
        MSG = msg.split(";")

        if MSG[0] == SocketsCodigos.SolicitudDenegada:
            print(MSG[1])
            Cerrar = False  # Salir de listener
            return

        if MSG[0] not in (SocketsCodigos.RecivirCartas, SocketsCodigos.CartaEnMesa):  # Imprimir mensaje recivido
            print(f"Mensaje recivido: {str(msg)}")

        if MSG[0] == SocketsCodigos.CartaEnMesa:
            print(f"La actual carta en Mesa es: {MSG[1]}")
            Textos = MSG[1].split(" ")
            tarjetaMesa = Tarjeta(Textos[0], int(Textos[1]))
            tarjetaMesa.x, tarjetaMesa.y = 520, 275
            imagen = pygame.image.load("Imagenes/Cartas/" + tarjetaMesa.nombre + ".png")  # Carta en Mesa
            tarjetaMesa.objTarjeta = pygame.transform.rotate(imagen, 90)

        if MSG[0] == SocketsCodigos.EnviarJugadores:
            Jugadores = json.loads(MSG[1])
            Rival = Jugadores[0]
        if MSG[0] == SocketsCodigos.RecivirCartas:
            contador = 0
            for carta in json.loads(MSG[1]):
                cartita = Tarjeta.convertirTarjetaAObjeto(carta)
                cartita.x, cartita.y = 110 + contador * 150, 530
                cartita.actual = False
                tarjetas.append(cartita)
                contador += 1
            cantidadDeTarjetas = len(tarjetas)
            [print(carta) for carta in tarjetas]
            armarTarjetas()

            pantallaActual = "Juego"
            textSurJugador = myfont.render(Jugador, False, Cl.BlANCO)
            textSurRival = myfont.render(Rival, False, Cl.BlANCO)
        if MSG[0] == SocketsCodigos.InidicarTurnoActual:  # Es el turno de este jugador
            print("Es tu turno")
            MiTurno = True
            SePidioCarta = False
            if len(tarjetas) < 7:
                MostrarPedirCarta = True
                MostrarSaltarTurno = False
            else:
                MostrarSaltarTurno = True
                MostrarPedirCarta = False

        if MSG[0] == SocketsCodigos.RecivirCarta:
            Textos = MSG[1].split(" ")
            TarjetaObjeto = Tarjeta(Textos[0], int(Textos[1]))
            tarjetas.append(TarjetaObjeto)
            armarTarjetas()
            #print(tarjetas[len(tarjetas)-1].nombre)
            #print(tarjetas[len(tarjetas)-1].objTarjeta)
            reOrdenarCoordenadasTarjetas()

        if MSG[0] == SocketsCodigos.MensajeJugadorPerdedor:
            pantallaActual = "Fin"
            TerminoJuego = True
            SeGano = False


def cambiarTarjetaActual(derecha):
    global tarjetaActual, cantidadDeTarjetas
    if derecha and tarjetaActual < cantidadDeTarjetas - 1:
        tarjetaActual += 1
    elif derecha and tarjetaActual == cantidadDeTarjetas - 1:
        tarjetaActual = 0
    elif not derecha and tarjetaActual > 0:
        tarjetaActual -= 1
    else:
        tarjetaActual = cantidadDeTarjetas - 1


def armarTarjetas():
    for tarjeta in tarjetas:
        tarjeta.objTarjeta = \
            pygame.image.load("Imagenes/Cartas/" + tarjeta.nombre + ".png")


def reOrdenarCoordenadasTarjetas():
    global cantidadDeTarjetas
    for i in range(len(tarjetas)):
        tarjetas[i].x = 110 + 150 * i
    cantidadDeTarjetas = len(tarjetas)


def pintar(display):
    global tarjetaMesa
    if pantallaActual == "Inicio":
        display.blit(fondoInicio, (0, 0))  # Fondo de pantalla

    if pantallaActual == "Fin":
        if SeGano:
            display.blit(fondoGanador, (0, 0))  # Fondo de pantalla Ganador
        else:
            display.blit(fondoPerdedor, (0, 0))  # Fondo de pantalla Perdedor

    elif pantallaActual == "Juego":
        display.blit(fondoJuego, (0, 0))  # Fondo de pantalla
        display.blit(textSurRival, (936, 165))
        display.blit(textSurJugador, (936, 380))

        if MiTurno: textoTurno = "Es tu turno"; x = 1000
        else: textoTurno = "Espere su turno"; x = 920
        display.blit(myfont.render(textoTurno, False, Cl.BlANCO), (x, 40))
        if MostrarPedirCarta: display.blit(myfont2.render("Pedir Carta", False, Cl.BlANCO), (270,270))
        if MostrarSaltarTurno: display.blit(myfont2.render("Saltar Turno", False, Cl.BlANCO), (260,270))

        for tarjeta in tarjetas:
            if tarjeta is not None and tarjeta.objTarjeta is not None:
                display.blit(tarjeta.objTarjeta, (tarjeta.x, tarjeta.y))  # Cartas Jugador
        if tarjetaMesa is not None and tarjetaMesa.objTarjeta is not None:
            display.blit(tarjetaMesa.objTarjeta, (tarjetaMesa.x, tarjetaMesa.y))  # Cartas en Mesa


def update():
    global MostrarPedirCarta
    global tarjetaMesa
    global MostrarSaltarTurno
    global pantallaActual, SeGano, TerminoJuego

    if pantallaActual == "Inicio":
        pass
    elif pantallaActual == "Juego":
        for i in range(len(tarjetas)):
            if i == tarjetaActual:
                tarjetas[i].actual = True
                tarjetas[i].y = 490
            else:
                tarjetas[i].actual = False
                tarjetas[i].y = 525
        if len(tarjetas) == 0: # Ya no le queda Cartas (GANO)
            EnviarMensaje(SocketsCodigos.MensajeJugadorGanador, "")
            pantallaActual = "Fin"
            SeGano = True
            TerminoJuego = True
    #if TerminoJuego:
     #   pantallaActual = "Fin"


def inputsUsuario():
    global Cerrar
    global cantidadDeTarjetas
    global MiTurno, MostrarPedirCarta, MostrarSaltarTurno
    global tarjetaActual

    if pantallaActual == "Inicio":
        for event in pygame.event.get():
            if event.type == QUIT:  # Salir de pygame
                CerrarConneccion()
                Cerrar = False
                pygame.quit()
                exit()

    elif pantallaActual == "Juego":
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:  # TECLAS
                if event.key == pygame.K_d:
                    cambiarTarjetaActual(True)
                if event.key == pygame.K_a:
                    cambiarTarjetaActual(False)

                if event.key == pygame.K_SPACE:
                    CartaValidad = FunctionsFinal.ValidarCarta(tarjetas[tarjetaActual], tarjetaMesa)
                    if CartaValidad and MiTurno:
                        tarjetaPaquete = Tarjeta.convertirTarjetaADict(tarjetas[tarjetaActual])
                        EnviarMensaje(SocketsCodigos.MandarCartaServidor, json.dumps(tarjetaPaquete))
                        tarjetas.pop(tarjetaActual)
                        reOrdenarCoordenadasTarjetas()
                        cantidadDeTarjetas = len(tarjetas)
                        MostrarPedirCarta = False
                        MostrarSaltarTurno = False
                        MiTurno = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mX,mY = pygame.mouse.get_pos()
                #print(mX,mY)
                if (250 <= mX <= 385) and (260 <= mY <= 440) and MiTurno:
                    if MostrarPedirCarta:
                        print("Se pidio una carta")
                        EnviarMensaje(SocketsCodigos.PedirCarta)
                        MostrarPedirCarta = False
                        MostrarSaltarTurno = True
                    elif MostrarSaltarTurno:
                        EnviarMensaje(SocketsCodigos.SaltarTurno)
                        MiTurno = False
                        MostrarSaltarTurno = False
                        MostrarPedirCarta = False

            if event.type == QUIT:  # Salir de pygame
                CerrarConneccion()
                Cerrar = False
                pygame.quit()
                exit()


def main():
    global socketCliente
    global ContinuarHilo
    global Jugador

    # Inicio del Juego
    Jugador = input("Hola, inserte su nombre para empezar el juego: ")
    ContinuarHilo = True

    socketCliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketCliente.connect(Connectar(False))

    # Crear Hilo para Escuchar
    listener = threading.Thread(target=Listener)
    listener.start()

    EnviarMensaje(SocketsCodigos.AgregarUsuario, Jugador)

    # Inicio de pygame
    pygame.init()
    display = pygame.display.set_mode((ResW, ResH), 0, 32)

    while not Cerrar:
        update()
        pintar(display)
        inputsUsuario()
        pygame.display.update()


main()
