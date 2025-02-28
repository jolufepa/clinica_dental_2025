# models/visita.py
from datetime import datetime

class Visita:
    def __init__(self, id_visita, identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado):
        self.id_visita = id_visita
        self.identificador = identificador
        self.fecha = datetime.strptime(fecha, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in fecha else fecha
        self.motivo = motivo
        self.diagnostico = diagnostico
        self.tratamiento = tratamiento
        self.odontologo = odontologo
        self.estado = estado

    @classmethod
    def from_tuple(cls, data_tuple):
        if len(data_tuple) < 8:
            raise ValueError("Datos insuficientes para crear una Visita")
        fecha_europea = datetime.strptime(data_tuple[2], "%Y-%m-%d").strftime("%d/%m/%y")
        return cls(data_tuple[0], data_tuple[1], fecha_europea, data_tuple[3], data_tuple[4], data_tuple[5], data_tuple[6], data_tuple[7])

    def __str__(self):
        return f"Visita(id={self.id_visita}, paciente={self.identificador}, fecha={self.fecha}, motivo={self.motivo}, odontologo={self.odontologo}, estado={self.estado})"