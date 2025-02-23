class Paciente:
    def __init__(self, identificador, nombre, fecha_nacimiento, telefono, email, direccion, historial):
        self.identificador = identificador
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.historial = historial
    
    @classmethod
    def from_tuple(cls, data_tuple):
        return cls(*data_tuple)