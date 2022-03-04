class Tarjeta:
    def __init__(self, color, valor):    # Crear Objeto
        self.x = 0
        self.y = 0
        self.actual = False
        self.nombre = color + str(valor)
        self.color = color
        self.valor = valor
        self.objTarjeta = None

    def __repr__(self):  #Imprimir Objeto
        return str(self.color + " " + str(self.valor))

    def convertirTarjetaADict(ObjetoTarjeta):
        return {"color": ObjetoTarjeta.color, "valor": ObjetoTarjeta.valor}

    def convertirTarjetaAObjeto(DicTarjeta):
        return Tarjeta(DicTarjeta["color"],DicTarjeta["valor"])


