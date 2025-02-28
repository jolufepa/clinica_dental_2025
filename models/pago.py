# models/pago.py

from datetime import datetime

class Pago:
    def __init__(self, id_pago, id_visita, identificador, monto_total, monto_pagado, fecha_pago, metodo, saldo):
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
        if len(data_tuple) < 8:
            raise ValueError("Datos insuficientes para crear un Pago")
        fecha_europea = datetime.strptime(data_tuple[5], "%Y-%m-%d").strftime("%d/%m/%y")
        return cls(data_tuple[0], data_tuple[1], data_tuple[2], data_tuple[3], data_tuple[4], fecha_europea, data_tuple[6], data_tuple[7])

    def __str__(self):
        return f"Pago(id={self.id_pago}, paciente={self.identificador}, fecha={self.fecha_pago}, monto_total=€{self.monto_total:.2f}, pagado=€{self.monto_pagado:.2f}, metodo={self.metodo}, saldo=€{self.saldo:.2f})"