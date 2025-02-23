class Cita:
    def __init__(self, id_cita, identificador, fecha, hora, odontologo, estado):
        self.id_cita = id_cita
        self.identificador = identificador
        self.fecha = fecha
        self.hora = hora
        self.odontologo = odontologo
        self.estado = estado

    @classmethod
    def from_tuple(cls, data_tuple):
        return cls(*data_tuple)