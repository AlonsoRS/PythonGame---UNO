import random
from Objetos import Tarjeta
Colores = ["Azul", "Amarillo", "Verde", "Rojo"]


def CrearCarta(Color, Valor):
    #return {"Color": Color, "Valor": Valor}
    #return [Color, Valor]
    return Tarjeta(str(Color), Valor)


def CrearMazo():
    mazo = []
    for Color in Colores:
        cartas_numero = [CrearCarta(Color, str(x+1)) for x in range(0, 9)]
        cartas_Mas2 = [CrearCarta(Color, "+2") for x in range(2)]
        cartas_Bloqueo = [CrearCarta(Color, "Bloqueo") for x in range(2)]
        cartas_Retorno = [CrearCarta(Color, "Retorno") for x in range(2)]
        mazo.append(CrearCarta(Color, 0))
        mazo.extend(cartas_numero*2)
        # mazo.extend(cartas_Mas2)
        # mazo.extend(cartas_Bloqueo)
        # mazo.extend(cartas_Retorno)

    Especiales_Mas4 = [CrearCarta("Especial", "+4") for x in range(4)]
    Especiales_CambiarColor = [CrearCarta("Especial", "CambiarColor") for x in range(4)]
    # mazo.extend(Especiales_Mas4)
    # mazo.extend(Especiales_CambiarColor)
    return mazo


def SuffleMazo(Mazo): #Fisher-Yates Shuffle
    for x in range(len(Mazo)-1, -1, -1):
        a = random.randint(0, x)
        if a != x:
            ValorA = Mazo[a]
            Mazo[a] = Mazo[x]
            Mazo[x] = ValorA
    return Mazo


def RepartirCartar(Mazo, nJugadores):
    CartasXJugador = []
    posActual = 0
    for n in range(nJugadores):
        CartasXJugador.append([])

    CartasARepartir = nJugadores*3
    for i in range(CartasARepartir):
        CartaActual = Mazo[0]
        CartasXJugador[posActual].append(CartaActual)
        if posActual < nJugadores-1:
            posActual += 1
        else:
            posActual = 0
        Mazo.pop(0)
    #Mazo = Mazo[:len(Mazo)-CartasARepartir]
    #for Jugador in CartasXJugador:
    #    for carta in Jugador:
    #        Mazo.remove(carta)
    return CartasXJugador


def ValidarCarta(cartaJugador, cartaEnMesa):
    resultado = False
    if cartaJugador.color == cartaEnMesa.color:
        resultado = True
    if int(cartaEnMesa.valor) == int(cartaJugador.valor):
        resultado = True
    #elif cartaJugador.color == "Especial":
        #resultado = True
    return resultado


def ConseguirCartaEnMesa(Mazo):
    cartaEnMesa = Mazo[0]
    Mazo.pop(0)
    return cartaEnMesa


def Prueba():
    Mazo = CrearMazo()
    #[print(Mazo[i], Mazo[i+1]) for i in range(0,len(Mazo)-1,2)]
    SuffleMazo(Mazo)
    print(f"Numero de cartas inciales: {len(Mazo)}.")
    #[print(f"I: {Mazo[i]}") for i in range(len(Mazo) - 1)]
    print(f"-----------")
    CartasRepartidas = RepartirCartar(Mazo, 2)
    [print(f"F: {Mazo[i]}") for i in range(len(Mazo) - 1)]
    [print(juego)for juego in CartasRepartidas]
    CartaEnMesa = ConseguirCartaEnMesa(Mazo)
    print(f"Numero de cartas restantes: {len(Mazo)}.")
    print("La carta en mesa es:", CartaEnMesa.nombre)
    print(f"La carta Azul 2 es compatible con mesa?",ValidarCarta(CrearCarta("Azul","2"),CartaEnMesa))


#Prueba()
