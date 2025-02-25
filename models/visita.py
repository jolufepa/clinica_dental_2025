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
        # Asegúrate de que data_tuple tenga 8 elementos (id_visita + los 7 atributos)
        if len(data_tuple) == 8:
            return cls(
                data_tuple[1],  # identificador
                data_tuple[2],  # fecha
                data_tuple[3],  # motivo
                data_tuple[4],  # diagnostico
                data_tuple[5],  # tratamiento
                data_tuple[6],  # odontologo
                data_tuple[7],  # estado
                data_tuple[0]   # id_visita
            )
        else:
            raise ValueError("Número incorrecto de campos en los datos de la visita")