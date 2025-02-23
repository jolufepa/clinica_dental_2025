class Receta:
    def __init__(self, id_receta, identificador, fecha, medicamento, dosis, instrucciones):
        self.id_receta = id_receta
        self.identificador = identificador
        self.fecha = fecha
        self.medicamento = medicamento
        self.dosis = dosis
        self.instrucciones = instrucciones

    @classmethod
    def from_tuple(cls, data_tuple):
        return cls(*data_tuple)