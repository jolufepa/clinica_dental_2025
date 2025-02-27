# models/pago.py
from datetime import datetime

class Pago:
    def __init__(self, id_pago, id_visita, identificador, monto_total, monto_pagado, fecha_pago, metodo, saldo):
        """
        Inicializa un objeto Pago con los datos proporcionados.
        
        Args:
            id_pago (int): Identificador único del pago.
            id_visita (int, optional): Identificador de la visita asociada (puede ser None).
            identificador (str): Identificador del paciente (DNI/NIE).
            monto_total (float): Monto total del pago.
            monto_pagado (float): Monto pagado.
            fecha_pago (str): Fecha del pago en formato DD/MM/YY (o YYYY-MM-DD internamente).
            metodo (str): Método de pago (Efectivo, Tarjeta, Transferencia, etc.).
            saldo (float): Saldo pendiente.
        """
        # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
        self.id_pago = id_pago
        self.id_visita = id_visita
        self.identificador = identificador
        self.monto_total = monto_total
        self.monto_pagado = monto_pagado
        self.fecha_pago = datetime.strptime(fecha_pago, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in fecha_pago else fecha_pago
        self.metodo = metodo
        self.saldo = saldo

    @classmethod
    def from_tuple(cls, data_tuple):
        """
        Crea una instancia de Pago a partir de una tupla de datos de la base de datos.
        
        Args:
            data_tuple: Tupla con los datos (id_pago, id_visita, identificador, monto_total, monto_pagado, fecha_pago, metodo, saldo).
        
        Returns:
            Pago: Instancia de la clase Pago.
        """
        if len(data_tuple) < 8:
            raise ValueError("Datos insuficientes para crear un Pago")
        # Convertir fecha de YYYY-MM-DD a DD/MM/YY para la salida
        fecha_europea = datetime.strptime(data_tuple[5], "%Y-%m-%d").strftime("%d/%m/%y")
        return cls(data_tuple[0], data_tuple[1], data_tuple[2], data_tuple[3], data_tuple[4], fecha_europea, data_tuple[6], data_tuple[7])

    def __str__(self):
        return f"Pago(id={self.id_pago}, paciente={self.identificador}, fecha={self.fecha_pago}, monto_total=€{self.monto_total:.2f}, pagado=€{self.monto_pagado:.2f}, metodo={self.metodo}, saldo=€{self.saldo:.2f})"