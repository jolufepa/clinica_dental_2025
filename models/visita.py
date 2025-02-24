# models/visita.py
class Visita:
    def __init__(self, identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado, id_visita=None):
        self.id_visita = id_visita  # Puede ser None al crear una nueva visita
        self.identificador = identificador
        self.fecha = fecha
        self.motivo = motivo
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.odontologo = odontologo
        self.estado = estado

    @classmethod
    def from_tuple(cls, data_tuple):
        return cls(*data_tuple)