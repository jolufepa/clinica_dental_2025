class Paciente:
    def __init__(self, identificador, nombre, fecha_nacimiento, telefono, email, direccion, historial, alergias="", tratamientos_previos="", notas=""):
        self.identificador = identificador
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.historial = historial
        self.alergias = alergias
        self.tratamientos_previos = tratamientos_previos
        self.notas = notas
    
    @classmethod
    def from_tuple(cls, data_tuple):
        # Ajusta según el número de campos en la base de datos
        return cls(*data_tuple[:7], data_tuple[7] if len(data_tuple) > 7 else "", 
                   data_tuple[8] if len(data_tuple) > 8 else "", 
                   data_tuple[9] if len(data_tuple) > 9 else "")  