# models/visita.py
from datetime import datetime

class Visita:
    def __init__(self, id_visita, identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado):
        """
        Inicializa un objeto Visita con los datos proporcionados.
        
        Args:
            id_visita (int): Identificador único de la visita.
            identificador (str): Identificador del paciente (DNI/NIE).
            fecha (str): Fecha de la visita en formato DD/MM/YY (o YYYY-MM-DD internamente).
            motivo (str): Motivo de la visita.
            diagnostico (str): Diagnóstico de la visita.
            tratamiento (str): Tratamiento realizado.
            odontologo (str): Odontólogo que atendió.
            estado (str): Estado de la visita (Pendiente, Completada, Cancelada).
        """
        # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
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
        """
        Crea una instancia de Visita a partir de una tupla de datos de la base de datos.
        
        Args:
            data_tuple: Tupla con los datos (id_visita, identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado).
        
        Returns:
            Visita: Instancia de la clase Visita.
        """
        if len(data_tuple) < 8:
            raise ValueError("Datos insuficientes para crear una Visita")
        # Convertir fecha de YYYY-MM-DD a DD/MM/YY para la salida
        fecha_europea = datetime.strptime(data_tuple[2], "%Y-%m-%d").strftime("%d/%m/%y")
        return cls(data_tuple[0], data_tuple[1], fecha_europea, data_tuple[3], data_tuple[4], data_tuple[5], data_tuple[6], data_tuple[7])

    def __str__(self):
        return f"Visita(id={self.id_visita}, paciente={self.identificador}, fecha={self.fecha}, motivo={self.motivo}, odontologo={self.odontologo}, estado={self.estado})"