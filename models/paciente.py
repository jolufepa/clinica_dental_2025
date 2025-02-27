# ARCHIVO models/paciente.py
class Paciente:
    def __init__(self, identificador, nombre, fecha_nacimiento, telefono, email, direccion, historial, alergias="", tratamientos_previos="", notas=""):
        self.identificador = identificador
        self.nombre = nombre
        self.fecha_nacimiento = fecha_nacimiento
        self.telefono = telefono  # Depuración
        print(f"Inicializando Paciente - Teléfono: {telefono} (type: {type(telefono)})")
        self.email = email
        self.direccion = direccion
        self.historial = historial
        self.alergias = alergias
        self.tratamientos_previos = tratamientos_previos
        self.notas = notas
    
    @classmethod
    def from_tuple(cls, data_tuple):
        # Ajusta según el número de campos en la base de datos
        print(f"Creando Paciente desde tupla: {data_tuple}")  # Depuración
        if len(data_tuple) < 7:
            raise ValueError("Datos insuficientes para crear un Paciente")
        instance = cls(*data_tuple[:7], data_tuple[7] if len(data_tuple) > 7 else "", 
                       data_tuple[8] if len(data_tuple) > 8 else "", 
                       data_tuple[9] if len(data_tuple) > 9 else "")
        print(f"Paciente creado - Teléfono: {instance.telefono} (type: {type(instance.telefono)})")
        return instance
    
    def __getattr__(self, name):
        # Depuración para detectar accesos fallidos
        print(f"Intentando acceder a atributo inexistente: {name}")
        raise AttributeError(f"'Paciente' object has no attribute '{name}'")