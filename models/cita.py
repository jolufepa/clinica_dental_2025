from datetime import datetime


class Cita:
    def __init__(self, id_cita, identificador, fecha, hora, odontologo, estado):
        # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
        self.id_cita = id_cita
        self.identificador = identificador
        self.fecha = datetime.strptime(fecha, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in fecha else fecha
        self.hora = hora
        self.odontologo = odontologo
        self.estado = estado

    @classmethod
    def from_tuple(cls, data_tuple):
        if len(data_tuple) < 6:
            raise ValueError("Datos insuficientes para crear una Cita")
        # Convertir fecha de YYYY-MM-DD a DD/MM/YY para la salida
        fecha_europea = datetime.strptime(data_tuple[2], "%Y-%m-%d").strftime("%d/%m/%y")
        return cls(data_tuple[0], data_tuple[1], fecha_europea, data_tuple[3], data_tuple[4], data_tuple[5])
    
    
    