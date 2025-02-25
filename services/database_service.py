# services/database_service.py
import sqlite3
from datetime import datetime
import threading
from models.paciente import Paciente
from models.visita import Visita
from models.pago import Pago
from models.receta import Receta
from models.cita import Cita
import bcrypt   # Importar bcrypt para encriptación de contraseñas
import smtplib
from email.mime.text import MIMEText

DEBUG = False  # Variable global para depuración


class DatabaseService:
    _instance = None
    _lock = threading.Lock()  # Añadir un lock para evitar concurrencia


    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._inicializar()
        return cls._instance

    # services/database_service.py
    def _inicializar(self):
        self.conn = sqlite3.connect("clinica_dental.db", check_same_thread=False)  # Permitir múltiples hilos
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
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
                historial TEXT,
                alergias TEXT,
                tratamientos_previos TEXT,
                notas TEXT
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
    
    def _asegurar_conexion_abierta(self):
        with self._lock:
            if self.conn is None:
                print("Reinicializando conexión a la base de datos...")
                self._inicializar()
            else:
                try:
                    # Intenta realizar una operación simple para verificar si la conexión está activa
                    self.cursor.execute("SELECT 1")
                except sqlite3.ProgrammingError:
                    print("Conexión cerrada, reinicializando...")
                    self._inicializar()
    # ================== OPERACIONES PARA PACIENTES ==================
    def guardar_paciente(self, paciente):
        self._asegurar_conexion_abierta()
        try:
            self.cursor.execute('''
            INSERT INTO pacientes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            paciente.identificador,
            paciente.nombre,
            paciente.fecha_nacimiento,
            paciente.telefono,
            paciente.email,
            paciente.direccion,
            paciente.historial,
            paciente.alergias,
            paciente.tratamientos_previos,
            paciente.notas
        ))
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("El paciente ya existe")

    def obtener_pacientes(self):
        self._asegurar_conexion_abierta()
        self.cursor.execute("SELECT * FROM pacientes")
        pacientes = self.cursor.fetchall()
        return [Paciente(*paciente) for paciente in pacientes]

    # services/database_service.py
    # En services/database_service.py
    def obtener_paciente(self, identificador):
        self._asegurar_conexion_abierta()
        self.cursor.execute("SELECT * FROM pacientes WHERE UPPER(identificador) = UPPER(?)", (identificador,))
        resultado = self.cursor.fetchone()
        if resultado:
            return Paciente(*resultado)
        return None
    
    # En services/database_service.py
    def actualizar_paciente(self, paciente):
        self._asegurar_conexion_abierta()
        with self._lock:
            try:
                if self.conn.in_transaction:
                    self.conn.rollback()
                self.cursor.execute('''
                    UPDATE pacientes SET
                        nombre = ?,
                        fecha_nacimiento = ?,
                        telefono = ?,
                        email = ?,
                        direccion = ?,
                        historial = ?,
                        alergias = ?,
                        tratamientos_previos = ?,
                        notas = ?
                    WHERE UPPER(identificador) = UPPER(?)
                ''', (
                    paciente.nombre,
                    paciente.fecha_nacimiento,
                    paciente.telefono,
                    paciente.email,
                    paciente.direccion,
                    paciente.historial,
                    paciente.alergias,
                    paciente.tratamientos_previos,
                    paciente.notas,
                    paciente.identificador
                ))
                if self.cursor.rowcount == 0:
                    raise ValueError("No se encontró el paciente con ese identificador")
                self.conn.commit()
            except sqlite3.Error as e:
                self.conn.rollback()
                raise Exception(f"Error al actualizar paciente: {str(e)}")
            finally:
                try:
                    if self.conn.in_transaction:
                        self.conn.commit()
                except sqlite3.Error:
                    pass

    def eliminar_paciente(self, identificador):
        self._asegurar_conexion_abierta()
        self.cursor.execute("DELETE FROM pacientes WHERE identificador = ?", (identificador,))
        self.conn.commit()

    def existe_identificador(self, identificador: str) -> bool:
        """Verifica si un identificador ya está registrado en la base de datos"""
        self.cursor.execute(
            "SELECT identificador FROM pacientes WHERE identificador = ?",
            (identificador,)
        )
        return self.cursor.fetchone() is not None
    
    
# ================== OPERACIONES PARA USUARIOS ================== 
          # Método para hashear contraseñas
    # services/database_service.py
    def _hash_password(self, password):
        """Hashea una contraseña usando bcrypt"""
        if not password or not isinstance(password, str):
            raise ValueError("La contraseña debe ser una cadena no vacía")
        try:
            # Asegurarnos de que la contraseña sea UTF-8 pura
            if not password.isascii():
                print(f"Advertencia: Contraseña contiene caracteres no ASCII: {password}")
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error al hashear la contraseña: {str(e)}")

    def _verify_password(self, password, hashed):
        """Verifica si una contraseña coincide con un hash bcrypt"""
        try:
            if not password or not isinstance(password, str):
                return False
            # Verificar si el hash es un hash bcrypt válido
            if not hashed.startswith('$2b$'):
                print(f"Advertencia: Hash no es un hash bcrypt válido: {hashed}")
                return False  # No es un hash bcrypt, asumir texto plano (para migración)
            print(f"Verificando contraseña: {password}, hash: {hashed}")
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            print(f"Error al verificar contraseña: {str(e)}")
            return False
    def crear_usuario(self, username, password, role):
        self._asegurar_conexion_abierta()
        try:
            hashed_password = self._hash_password(password)
            self.cursor.execute(
                "INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)",
                (username, hashed_password, role)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("El usuario ya existe")

    def verificar_usuario(self, username, password):
        """Verifica credenciales y retorna el role si existe, None si no"""
        self._asegurar_conexion_abierta()
        try:
            with self._lock:
                self.cursor.execute(
                    "SELECT password, role FROM usuarios WHERE username = ?",
                    (username,)
                )
                result = self.cursor.fetchone()
                if result:
                    hashed_password, role = result
                    print(f"Verificando usuario {username}, hash almacenado: {hashed_password}, contraseña ingresada: {password}")
                    if self._verify_password(password, hashed_password):
                        return role
                return None
        except sqlite3.Error as e:
            raise Exception(f"Error al verificar usuario: {str(e)}")

    def actualizar_usuario(self, username, password, role):
        self._asegurar_conexion_abierta()
        try:
            with self._lock:
                self.conn.execute("BEGIN TRANSACTION")
                if password:
                    hashed_password = self._hash_password(password)
                    print(f"Guardando hash para {username}: {hashed_password}")
                    self.cursor.execute(
                        "UPDATE usuarios SET password = ?, role = ? WHERE username = ?",
                        (hashed_password, role, username)
                    )
                else:
                    self.cursor.execute(
                        "UPDATE usuarios SET role = ? WHERE username = ?",
                        (role, username)
                    )
                self.conn.commit()
                if self.cursor.rowcount == 0:
                    raise ValueError("Usuario no encontrado")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al actualizar usuario: {str(e)}")


    def eliminar_usuario(self, username):
        self._asegurar_conexion_abierta()
        try:
            self.cursor.execute(
                "DELETE FROM usuarios WHERE username = ?",
                (username,)
            )
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError("Usuario no encontrado")
        except sqlite3.Error as e:
            raise Exception(f"Error al eliminar usuario: {str(e)}")
    def restaurar_password_admin(self):
        self._asegurar_conexion_abierta()
        try:
            default_password = "admin123"  # O la contraseña que desees
            hashed_password = self._hash_password(default_password)
            self.cursor.execute(
                "UPDATE usuarios SET password = ? WHERE username = 'admin1'",
                (hashed_password,)
            )
            self.conn.commit()
            print("Contraseña de admin1 restaurada a:", default_password)
        except sqlite3.Error as e:
            raise Exception(f"Error al restaurar contraseña: {str(e)}")    
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
        self._asegurar_conexion_abierta()
        try:
            with self._lock:
                hashed_password = self._hash_password(password)
                self.cursor.execute(
                    "INSERT INTO usuarios (username, password, role) VALUES (?, ?, ?)",
                    (username, hashed_password, role)
                )
                self.conn.commit()
        except sqlite3.IntegrityError:
            raise ValueError("El usuario ya existe")
        except sqlite3.Error as e:
            raise Exception(f"Error al crear usuario: {str(e)}")
    def _crear_usuario_base(self, username, password, role):
        """Método auxiliar para inicializar usuarios base, manejando errores"""
        try:
            self._asegurar_conexion_abierta()
            with self._lock:
                self.cursor.execute(
                    "INSERT OR IGNORE INTO usuarios (username, password, role) VALUES (?, ?, ?)",
                    (username, self._hash_password(password), role)
                )
                self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Usuario {username} ya existe, saltando creación")
        except sqlite3.Error as e:
            raise Exception(f"Error al crear usuario base: {str(e)}")
    def verificar_usuario(self, username, password):
        self._asegurar_conexion_abierta()
        try:
            with self._lock:
                self.cursor.execute(
                    "SELECT password, role FROM usuarios WHERE username = ?",
                    (username,)
                )
                result = self.cursor.fetchone()
                if result:
                    hashed_password, role = result
                    print(f"Verificando usuario {username}, hash almacenado: {hashed_password}, contraseña ingresada: {password}")
                    if self._verify_password(password, hashed_password):
                        return role
                return None
        except sqlite3.Error as e:
            raise Exception(f"Error al verificar usuario: {str(e)}")
        
    
    # services/database_service.py
    def guardar_vista(self, visita):
        try:
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
        except Exception as e:
            print(f"Error al guardar visita: {str(e)}")
            return False 
          
    # services/database_service.py
    def obtener_visitas(self, paciente_id: str):
        self._asegurar_conexion_abierta()
        try:
            # Especificar explícitamente los campos en el orden que espera Visita
            self.cursor.execute(
                "SELECT id_visita, identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado FROM visitas WHERE identificador = ?", 
                (paciente_id,)
            )
            visitas = self.cursor.fetchall()
            print(f"Datos raw de visitas desde la base de datos: {visitas}")  # Depuración
            return [Visita.from_tuple(visita) for visita in visitas]  # Usar from_tuple explícitamente
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener visitas: {str(e)}")
        
    # services/database_service.py
    def restaurar_password_admin(self):
        self._asegurar_conexion_abierta()
        try:
            with self._lock:
                default_password = "admin123"  # Contraseña predeterminada
                hashed_password = self._hash_password(default_password)
                self.cursor.execute(
                    "UPDATE usuarios SET password = ? WHERE username = 'admin1'",
                    (hashed_password,)
                )
                self.conn.commit()
                if self.cursor.rowcount == 0:
                    raise ValueError("Usuario admin1 no encontrado")
                print("Contraseña de admin1 restaurada a:", default_password)
        except sqlite3.Error as e:
            raise Exception(f"Error al restaurar contraseña: {str(e)}")     
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
        self._asegurar_conexion_abierta()
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
    # services/database_service.py
    def cerrar_conexion(self):
        with self._lock:
            if self.conn is not None:
                try:
                    self.conn.close()
                except sqlite3.ProgrammingError:
                    pass
                finally:
                    self.conn = None
                    self.cursor = None


    def enviar_notificacion_cita(self, paciente_email, cita_fecha, cita_hora):
        try:
            msg = MIMEText(f"Recordatorio de cita: Fecha: {cita_fecha}, Hora: {cita_hora}")
            msg['Subject'] = 'Recordatorio de Cita Dental'
            msg['From'] = 'jolufepa@gmail.com'
            msg['To'] = paciente_email

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login('tu_email@example.com', 'tu_password_app')  # Usa una contraseña de aplicación para Gmail
                server.send_message(msg)
        except Exception as e:
            raise Exception(f"Error al enviar notificación: {str(e)}")
    # In services/database_service.py, add this method to the DatabaseService class
    def buscar_pacientes(self, texto_busqueda):
        """
        Busca pacientes por identificador o nombre (puedes expandir la búsqueda a otros campos si es necesario).
        """
        self._asegurar_conexion_abierta()
        try:
            # Buscar por identificador (case-insensitive) o nombre
            self.cursor.execute("""
                SELECT * FROM pacientes 
                WHERE UPPER(identificador) LIKE UPPER(?) 
                OR UPPER(nombre) LIKE UPPER(?)
            """, (f"%{texto_busqueda}%", f"%{texto_busqueda}%"))
            pacientes = self.cursor.fetchall()
            return [Paciente(*paciente) for paciente in pacientes]
        except sqlite3.Error as e:
            raise Exception(f"Error al buscar pacientes: {str(e)}")