import datetime
import os.path
from os import path

def DatosdePartida (x, y, z):
  fecha=datetime.datetime.now()
  datos=open("Jugadores.txt", "a+")
  cadena="\n"+ '{:<10}'.format(x) + "       "+ '{:<10}'.format(y) + "       " + '{:<10}'.format(z)+"     "+'{:<40}'.format(fecha.strftime("%Y-%m-%d %H:%M:%S"))
  datos.write(cadena)
  datos.close()

def CrearArchivo():
  datos=open("Jugadores.txt", "a+")
  cadena='{:<10}'.format('Jugador 1')
  datos.write(cadena)
  datos.write("       ")
  cadena='{:<10}'.format('Jugador 2')
  datos.write(cadena)
  datos.write("       ")
  cadena='{:<10}'.format('Ganador')
  datos.write(cadena)
  datos.write("     ")
  cadena='{:<15}'.format('Date')
  datos.write(cadena)
  datos.close()

def Verificar(x,y,z):
  a = path.exists("Jugadores.txt")
  if a == True:
    return DatosdePartida(x, y, z)
  else:
    return CrearArchivo(), DatosdePartida(x, y, z)