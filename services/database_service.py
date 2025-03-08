# ARCHIVO  services/database_service.py
import json
import sqlite3
from datetime import datetime
import threading
from tkinter import messagebox
from models.paciente import Paciente
from models.visita import Visita
from models.pago import Pago
from models.receta import Receta
from models.cita import Cita
from models.odontograma import Odontograma
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
            CREATE TABLE IF NOT EXISTS odontogramas (
                paciente_id TEXT PRIMARY KEY,
                datos TEXT,  -- JSON con el estado de los dientes
                FOREIGN KEY (paciente_id) REFERENCES pacientes(identificador)
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
                    
                    
    def obtener_registros_por_fecha(self, concepto, paciente_id=None, fecha_inicio=None, fecha_fin=None):
        """Obtiene registros (citas, visitas o pagos) filtrados por rango de fechas y paciente_id, incluyendo nombre del paciente."""
        self._asegurar_conexion_abierta()
        try:
            if concepto == "citas":
                query = "SELECT c.*, p.nombre FROM citas c JOIN pacientes p ON c.identificador = p.identificador WHERE 1=1"
                params = []
                if paciente_id:
                    query += " AND c.identificador = ?"
                    params.append(paciente_id)
                if fecha_inicio or fecha_fin:
                    query += " AND c.fecha BETWEEN ? AND ?"
                    params.extend([fecha_inicio or "1970-01-01", fecha_fin or datetime.now().strftime("%Y-%m-%d")])
                self.cursor.execute(query, params)
                return self.cursor.fetchall()  # Tuplas con (id_cita, identificador, fecha, hora, odontologo, estado, nombre)
            elif concepto == "visitas":
                query = "SELECT v.*, p.nombre FROM visitas v JOIN pacientes p ON v.identificador = p.identificador WHERE 1=1"
                params = []
                if paciente_id:
                    query += " AND v.identificador = ?"
                    params.append(paciente_id)
                if fecha_inicio or fecha_fin:
                    query += " AND v.fecha BETWEEN ? AND ?"
                    params.extend([fecha_inicio or "1970-01-01", fecha_fin or datetime.now().strftime("%Y-%m-%d")])
                self.cursor.execute(query, params)
                return self.cursor.fetchall()  # Tuplas con (id_visita, identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado, nombre)
            elif concepto == "pagos":
                query = "SELECT p.*, pa.nombre FROM pagos p JOIN pacientes pa ON p.identificador = pa.identificador WHERE 1=1"
                params = []
                if paciente_id:
                    query += " AND p.identificador = ?"
                    params.append(paciente_id)
                if fecha_inicio or fecha_fin:
                    query += " AND p.fecha_pago BETWEEN ? AND ?"
                    params.extend([fecha_inicio or "1970-01-01", fecha_fin or datetime.now().strftime("%Y-%m-%d")])
                self.cursor.execute(query, params)
                return self.cursor.fetchall()  # Tuplas con (id_pago, id_visita, identificador, monto_total, monto_pagado, fecha_pago, metodo, saldo, nombre)
            else:
                raise ValueError("Concepto no válido. Use 'citas', 'visitas' o 'pagos'")
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener registros: {str(e)}")                
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
    def obtener_nombre_paciente(self, identificador):
        """Obtiene el nombre del paciente por su identificador."""
        self._asegurar_conexion_abierta()
        try:
            self.cursor.execute("SELECT nombre FROM pacientes WHERE identificador = ?", (identificador,))
            result = self.cursor.fetchone()
            return result[0] if result else "Desconocido"
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener nombre del paciente: {str(e)}")


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
        """Elimina un paciente específico por su identificador, manejando errores y transacciones."""
        self._asegurar_conexion_abierta()
        try:
            # Verificar que el paciente existe antes de intentar eliminar
            self.cursor.execute("SELECT identificador FROM pacientes WHERE identificador = ?", (identificador,))
            if not self.cursor.fetchone():
                raise ValueError(f"No se encontró el paciente con identificador {identificador}")

            # Ejecutar la eliminación
            self.cursor.execute("DELETE FROM pacientes WHERE identificador = ?", (identificador,))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError(f"No se pudo eliminar el paciente con identificador {identificador}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al eliminar paciente: {str(e)}")
    
    
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
        """Guarda una nueva cita en la base de datos."""
        try:
            # Verificar si el paciente existe
            self.cursor.execute(
                "SELECT identificador FROM pacientes WHERE identificador = ?",
                (cita.identificador,)
            )
            if not self.cursor.fetchone():
                raise ValueError("El paciente no existe")

            # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
            fecha_sql = datetime.strptime(cita.fecha, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in cita.fecha else cita.fecha

            # Insertar cita
            self.cursor.execute("""
                INSERT INTO citas 
                (identificador, fecha, hora, odontologo, estado)
                VALUES (?, ?, ?, ?, ?)
            """, (
                cita.identificador,
                fecha_sql,
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
        """Obtiene todas las citas o las citas de un paciente específico."""
        try:
            if paciente_id:
                self.cursor.execute(
                    "SELECT * FROM citas WHERE identificador = ?",
                    (paciente_id,)
                )
            else:
                self.cursor.execute("SELECT * FROM citas")
            citas = self.cursor.fetchall()
            return [Cita(*cita) for cita in citas]  # No convertimos aquí, lo haremos en el modelo o vista
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener citas: {str(e)}")
    def actualizar_cita(self, cita):
        """Actualiza una cita específica en la base de datos."""
        self._asegurar_conexion_abierta()
        try:
            # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
            fecha_sql = datetime.strptime(cita.fecha, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in cita.fecha else cita.fecha

            self.cursor.execute("""
                UPDATE citas SET fecha = ?, hora = ?, odontologo = ?, estado = ?
                WHERE id_cita = ?
            """, (fecha_sql, cita.hora, cita.odontologo, cita.estado, cita.id_cita))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError(f"No se encontró la cita con ID {cita.id_cita}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al actualizar cita: {str(e)}")   

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
    def guardar_visita(self, visita):
        """Guarda una nueva visita en la base de datos."""
        try:
            # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
            fecha_sql = datetime.strptime(visita.fecha, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in visita.fecha else visita.fecha

            self.cursor.execute("""
                INSERT INTO visitas 
                (identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                visita.identificador,
                fecha_sql,
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
            self.cursor.execute(
                "SELECT id_visita, identificador, fecha, motivo, diagnostico, tratamiento, odontologo, estado FROM visitas WHERE identificador = ?",
                (paciente_id,)
            )
            visitas = self.cursor.fetchall()
            return [Visita.from_tuple(visita) for visita in visitas]  # No convertimos aquí
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener visitas: {str(e)}")
    def actualizar_visita(self, visita):
        """Actualiza una visita específica en la base de datos."""
        self._asegurar_conexion_abierta()
        try:
            # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
            fecha_sql = datetime.strptime(visita.fecha, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in visita.fecha else visita.fecha

            self.cursor.execute("""
                UPDATE visitas SET fecha = ?, motivo = ?, diagnostico = ?, tratamiento = ?, odontologo = ?, estado = ?
                WHERE id_visita = ?
            """, (fecha_sql, visita.motivo, visita.diagnostico, visita.tratamiento, visita.odontologo, visita.estado, visita.id_visita))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError(f"No se encontró la visita con ID {visita.id_visita}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al actualizar visita: {str(e)}")   
        
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
        """Guarda un nuevo pago en la base de datos."""
        try:
            # Verificar si el paciente existe
            self.cursor.execute(
                "SELECT identificador FROM pacientes WHERE identificador = ?",
                (pago.identificador,)
            )
            if not self.cursor.fetchone():
                raise ValueError("El paciente no existe")

            # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
            fecha_sql = datetime.strptime(pago.fecha_pago, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in pago.fecha_pago else pago.fecha_pago

            # Insertar pago
            self.cursor.execute("""
                INSERT INTO pagos 
                (id_visita, identificador, monto_total, monto_pagado, fecha_pago, metodo, saldo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pago.id_visita,
                pago.identificador,
                pago.monto_total,
                pago.monto_pagado,
                fecha_sql,
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
            return [Pago(*pago) for pago in pagos]  # No convertimos aquí
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener pagos: {str(e)}")
    def actualizar_pago(self, pago):
        """Actualiza un pago específico en la base de datos."""
        self._asegurar_conexion_abierta()
        try:
            # Convertir fecha de DD/MM/YY a YYYY-MM-DD si es necesario
            fecha_sql = datetime.strptime(pago.fecha_pago, "%d/%m/%y").strftime("%Y-%m-%d") if '/' in pago.fecha_pago else pago.fecha_pago

            self.cursor.execute("""
                UPDATE pagos SET id_visita = ?, identificador = ?, monto_total = ?, monto_pagado = ?, fecha_pago = ?, metodo = ?, saldo = ?
                WHERE id_pago = ?
            """, (pago.id_visita, pago.identificador, pago.monto_total, pago.monto_pagado, fecha_sql, pago.metodo, pago.saldo, pago.id_pago))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError(f"No se encontró el pago con ID {pago.id_pago}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al actualizar pago: {str(e)}")  
    
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
    def buscar_paciente(self, texto_busqueda):
        """
        Busca un paciente por Identificador, Nombre o Teléfono (case-insensitive), manejando formatos especiales.
        """
        self._asegurar_conexion_abierta()
        try:
            # Depuración: Imprimir el texto de búsqueda
            print(f"Buscando paciente con: {texto_busqueda}")
            
            # Limpiar el texto de búsqueda (eliminar guiones, espacios, etc.)
            texto_limpio = texto_busqueda.replace("-", "").replace(" ", "")
            
            # Buscar por Identificador, Nombre o Teléfono
            query = """
                SELECT * FROM pacientes 
                WHERE UPPER(identificador) LIKE UPPER(?) 
                OR UPPER(nombre) LIKE UPPER(?) 
                OR UPPER(REPLACE(REPLACE(telefono, '-', ''), ' ', '')) LIKE UPPER(?)
            """
            self.cursor.execute(query, (f"%{texto_busqueda}%", f"%{texto_busqueda}%", f"%{texto_limpio}%"))
            resultado = self.cursor.fetchone()
            
            if resultado:
                print(f"Paciente encontrado (tupla): {resultado}")  # Depuración detallada
                try:
                    paciente = Paciente(*resultado)
                    print(f"Paciente creado: Identificador={paciente.identificador}, Teléfono={paciente.telefono}")
                    return paciente
                except Exception as e:
                    print(f"Error al crear Paciente desde tupla: {str(e)}")
                    raise Exception(f"Error al procesar paciente: {str(e)}")
            print("No se encontró ningún paciente")  # Depuración
            return None
        except sqlite3.Error as e:
            print(f"Error SQL al buscar paciente: {str(e)}")  # Depuración
            raise Exception(f"Error al buscar paciente: {str(e)}")

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
    def eliminar_cita(self, id_cita):
        """Elimina una cita específica por su ID."""
        self._asegurar_conexion_abierta()
        try:
            self.cursor.execute("DELETE FROM citas WHERE id_cita = ?", (id_cita,))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError(f"No se encontró la cita con ID {id_cita}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al eliminar cita: {str(e)}")

    def eliminar_visita(self, id_visita):
        """Elimina una visita específica por su ID."""
        self._asegurar_conexion_abierta()
        try:
            self.cursor.execute("DELETE FROM visitas WHERE id_visita = ?", (id_visita,))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError(f"No se encontró la visita con ID {id_visita}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al eliminar visita: {str(e)}")

    def eliminar_pago(self, id_pago):
        """Elimina un pago específico por su ID."""
        self._asegurar_conexion_abierta()
        try:
            self.cursor.execute("DELETE FROM pagos WHERE id_pago = ?", (id_pago,))
            self.conn.commit()
            if self.cursor.rowcount == 0:
                raise ValueError(f"No se encontró el pago con ID {id_pago}")
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Error al eliminar pago: {str(e)}")
        
    def obtener_pagos_mes(self, mes_ano=None):
        """Obtiene los pagos del mes y año especificados (formato 'YYYY-MM') o del mes actual por defecto."""
        self._asegurar_conexion_abierta()
        try:
            if not mes_ano:
                from datetime import datetime
                mes_ano = datetime.now().strftime("%Y-%m")
            self.cursor.execute(
                "SELECT * FROM pagos WHERE strftime('%Y-%m', fecha_pago) = ?",
                (mes_ano,)
            )
            pagos = self.cursor.fetchall()
            return [Pago(*pago) for pago in pagos]
        except sqlite3.Error as e:
            raise Exception(f"Error al obtener pagos del mes: {str(e)}")
    def guardar_odontograma(self, odontograma):
        self._asegurar_conexion_abierta()
        try:
            datos_json = json.dumps(odontograma.to_dict()["dientes"])
            print(f"Guardando odontograma: paciente_id={odontograma.paciente_id}, datos_json={datos_json}")
            self.cursor.execute(
                "INSERT OR REPLACE INTO odontogramas (paciente_id, datos) VALUES (?, ?)",
                (odontograma.paciente_id, datos_json)
            )
            self.conn.commit()
            print("Odontograma guardado en la base de datos.")
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error SQL al guardar odontograma: {str(e)}")
            raise Exception(f"Error al guardar odontograma: {str(e)}")
        except json.JSONEncodeError as e:
            print(f"Error al codificar JSON del odontograma: {str(e)}")
            raise Exception(f"Error al codificar odontograma: {str(e)}")

    def obtener_odontograma(self, paciente_id):
        self._asegurar_conexion_abierta()
        try:
            self.cursor.execute("SELECT datos FROM odontogramas WHERE paciente_id = ?", (paciente_id,))
            result = self.cursor.fetchone()
            if result:
                datos = json.loads(result[0])
                print(f"Datos deserializados del odontograma: {datos}")
                return Odontograma(paciente_id, datos)
            print(f"No se encontró odontograma para paciente_id: {paciente_id}, creando nuevo.")
            return Odontograma(paciente_id)
        except sqlite3.Error as e:
            print(f"Error SQL al obtener odontograma: {str(e)}")
            raise Exception(f"Error al obtener odontograma: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON del odontograma: {str(e)}")
            raise Exception(f"Error al decodificar odontograma: {str(e)}")
        except Exception as e:
            print(f"Error inesperado en obtener_odontograma: {str(e)} - Stack: {str(e)}")
            raise