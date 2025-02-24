# services/database_service.py
import sqlite3
from datetime import datetime
from models.paciente import Paciente
from models.visita import Visita
from models.pago import Pago
from models.receta import Receta
from models.cita import Cita

class DatabaseService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._inicializar()
        return cls._instance

    # services/database_service.py
    def _inicializar(self):
        self.conn = sqlite3.connect("clinica_dental.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")  # ← Activa claves foráneas
        self._crear_tablas()

    def _crear_tablas(self):
        #"""Crea todas las tablas necesarias"""
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS pacientes (
                identificador TEXT PRIMARY KEY,
                nombre TEXT,
                fecha_nacimiento TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                historial TEXT
            );

            CREATE TABLE IF NOT EXISTS visitas (
                id_visita INTEGER PRIMARY KEY AUTOINCREMENT,
                identificador TEXT,
                fecha TEXT,
                motivo TEXT,
                diagnostico TEXT,
                tratamiento TEXT,
                odontologo TEXT,
                estado TEXT,
                FOREIGN KEY (identificador) REFERENCES pacientes(identificador)
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT PRIMARY KEY,
                password TEXT,
                role TEXT CHECK(role IN ('admin', 'recepcion'))
            );
             CREATE TABLE IF NOT EXISTS pagos (
                id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                id_visita INTEGER,
                identificador TEXT,
                monto_total REAL,
                monto_pagado REAL,
                fecha_pago TEXT,
                metodo TEXT,
                saldo REAL,
                FOREIGN KEY (identificador) REFERENCES pacientes(identificador),
                FOREIGN KEY (id_visita) REFERENCES visitas(id_visita)
            );
            CREATE TABLE IF NOT EXISTS citas (
                    id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
                    identificador TEXT,
                    fecha TEXT,
                    hora TEXT,
                    odontologo TEXT,
                    estado TEXT,
                    FOREIGN KEY (identificador) REFERENCES pacientes(identificador)
                );
            ''')
        self.conn.commit()
        

    # ================== OPERACIONES PARA PACIENTES ==================
    def guardar_paciente(self, paciente):
        try:
            self.cursor.execute('''
                INSERT INTO pacientes VALUES (
                    ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                paciente.identificador,
                paciente.nombre,
                paciente.fecha_nacimiento,
                paciente.telefono,
                paciente.email,
                paciente.direccion,
                paciente.historial
            ))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("El paciente ya existe")

    def obtener_pacientes(self):
        """Obtiene todos los pacientes registrados"""
        self.cursor.execute("SELECT * FROM pacientes")
        pacientes = self.cursor.fetchall()
        return [Paciente(*paciente) for paciente in pacientes]

    def obtener_paciente(self, identificador):
        """Obtiene un paciente específico por su identificador"""
        try:
            self.cursor.execute("SELECT * FROM pacientes WHERE identificador = ?", (identificador,))
            resultado = self.cursor.fetchone()
            if resultado:
                return Paciente(*resultado)  # Usa el modelo Paciente para crear el objeto
            return None  # Si no se encuentra el paciente
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener paciente: {str(e)}")

    def actualizar_paciente(self, paciente):
        self.cursor.execute('''
            UPDATE pacientes SET
                nombre = ?,
                fecha_nacimiento = ?,
                telefono = ?,
                email = ?,
                direccion = ?,
                historial = ?
            WHERE identificador = ?
        ''', (
            paciente.nombre,
            paciente.fecha_nacimiento,
            paciente.telefono,
            paciente.email,
            paciente.direccion,
            paciente.historial,
            paciente.identificador
        ))
        self.conn.commit()

    def eliminar_paciente(self, identificador):
        self.cursor.execute("DELETE FROM pacientes WHERE identificador = ?", (identificador,))
        self.conn.commit()

    def existe_identificador(self, identificador: str) -> bool:
        """Verifica si un identificador ya está registrado en la base de datos"""
        self.cursor.execute(
            "SELECT identificador FROM pacientes WHERE identificador = ?",
            (identificador,)
        )
        return self.cursor.fetchone() is not None
# ================== OPERACIONES PARA CITAS ==================
    def guardar_cita(self, cita):
        """Guarda una nueva cita en la base de datos"""
        try:
            # Verificar si el paciente existe
            self.cursor.execute(
                "SELECT identificador FROM pacientes WHERE identificador = ?",
                (cita.identificador,)
            )
            if not self.cursor.fetchone():
                raise ValueError("El paciente no existe")

            # Insertar cita
            self.cursor.execute('''
                INSERT INTO citas 
                (identificador, fecha, hora, odontologo, estado)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                cita.identificador,
                cita.fecha,
                cita.hora,
                cita.odontologo,
                cita.estado
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {str(e)}")
            return False
        except ValueError as e:
            print(f"Error de validación: {str(e)}")
            return False

    def obtener_citas(self, paciente_id: str = None):
        """Obtiene todas las citas o las citas de un paciente específico"""
        try:
            if paciente_id:
                self.cursor.execute(
                    "SELECT * FROM citas WHERE identificador = ?",
                    (paciente_id,)
                )
            else:
                self.cursor.execute("SELECT * FROM citas")
            citas = self.cursor.fetchall()
            return [Cita(*cita) for cita in citas]  # Convierte a objetos Cita
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener citas: {str(e)}")

    def verificar_disponibilidad_cita(self, fecha: str, hora: str, odontologo: str) -> bool:
        """Verifica si un odontólogo está disponible en una fecha y hora específicas"""
        try:
            self.cursor.execute(
                "SELECT COUNT(*) FROM citas WHERE fecha = ? AND hora = ? AND odontologo = ? AND estado != 'Cancelada'",
                (fecha, hora, odontologo)
            )
            count = self.cursor.fetchone()[0]
            return count == 0  # Retorna True si no hay conflictos (disponible)
        except sqlite3.Error as e:
            raise Exception(f"Error al verificar disponibilidad: {str(e)}")
    # ================== OPERACIONES PARA USUARIOS ==================
    def crear_usuario(self, username, password, role):
        self.cursor.execute(
            "INSERT INTO usuarios VALUES (?, ?, ?)",
            (username, password, role)
        )
        self.conn.commit()

    def verificar_usuario(self, username, password):
        #"""Verifica credenciales sin cerrar la conexión"""
        try:
            self.cursor.execute(
                "SELECT role FROM usuarios WHERE username = ? AND password = ?",
                (username, password)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.ProgrammingError:
            self._inicializar()  # Reabre conexión si está cerrada
            return self.verificar_usuario(username, password)
        
    # services/database_service.py
    # services/database_service.py
    def guardar_vista(self, visita):
        try:
            # Verificar si el paciente existe
            self.cursor.execute(
                "SELECT identificador FROM pacientes WHERE identificador = ?",
                (visita.identificador,)
            )
            if not self.cursor.fetchone():
                raise ValueError("El paciente no existe")  # Error personalizado

            # Insertar visita
            self.cursor.execute('''
                INSERT INTO visitas 
                (identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                visita.identificador,
                visita.fecha,
                visita.motivo,
                visita.diagnostico,
                visita.tratamiento,
                visita.odontologo,
                visita.estado
            ))
            self.conn.commit()
            return True

        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {str(e)}")
            return False
        except ValueError as e:
            print(f"Error de validación: {str(e)}")
            return False 
          
    # services/database_service.py
    def obtener_visitas(self, paciente_id: str):
        """Obtiene todas las visitas de un paciente específico"""
        try:
            self.cursor.execute(
                "SELECT * FROM visitas WHERE identificador = ?", 
                (paciente_id,)
            )
            visitas = self.cursor.fetchall()
            return [Visita(*visita) for visita in visitas]  # Convierte a objetos Visita
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener visitas: {str(e)}")
        
        
    # ================== OPERACIONES PARA PAGOS ==================
    def guardar_pago(self, pago):
        """Guarda un nuevo pago en la base de datos"""
        try:
            # Verificar si el paciente existe
            self.cursor.execute(
                "SELECT identificador FROM pacientes WHERE identificador = ?",
                (pago.identificador,)
            )
            if not self.cursor.fetchone():
                raise ValueError("El paciente no existe")

            # Insertar pago
            self.cursor.execute('''
                INSERT INTO pagos 
                (id_visita, identificador, monto_total, monto_pagado, fecha_pago, metodo, saldo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pago.id_visita,  # Puede ser None si no se vincula a una visita aún
                pago.identificador,
                pago.monto_total,
                pago.monto_pagado,
                pago.fecha_pago,
                pago.metodo,
                pago.saldo
            ))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {str(e)}")
            return False
        except ValueError as e:
            print(f"Error de validación: {str(e)}")
            return False

    def obtener_pagos(self, paciente_id: str = None):
        """Obtiene todos los pagos o los pagos de un paciente específico"""
        try:
            if paciente_id:
                self.cursor.execute(
                    "SELECT * FROM pagos WHERE identificador = ?",
                    (paciente_id,)
                )
            else:
                self.cursor.execute("SELECT * FROM pagos")
            pagos = self.cursor.fetchall()
            return [Pago(*pago) for pago in pagos]  # Convierte a objetos Pago
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener pagos: {str(e)}")
    
    # ================== MÉTODOS ADICIONALES ==================
    def cerrar_conexion(self):
        #"""Cierra la conexión solo al finalizar la aplicación"""
        if self.conn:
            self.conn.close()
          

   