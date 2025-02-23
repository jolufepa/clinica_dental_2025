class Pago:
    def __init__(self, id_pago, id_visita, identificador, monto_total, monto_pagado, fecha_pago, metodo, saldo):
        self.id_pago = id_pago
        self.id_visita = id_visita
        self.identificador = identificador
        self.monto_total = monto_total
        self.monto_pagado = monto_pagado
        self.fecha_pago = fecha_pago
        self.metodo = metodo
        self.saldo = saldo

    @classmethod
    def from_tuple(cls, data_tuple):
        return cls(*data_tuple)