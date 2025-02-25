import sqlite3
from services.database_service import DatabaseService
import bcrypt

db = DatabaseService()
conn = db.conn
cursor = db.cursor

cursor.execute("SELECT username, password FROM usuarios")
usuarios = cursor.fetchall()

for username, password in usuarios:
    if not password.startswith('$2b$'):  # Verificar si es texto plano, no un hash bcrypt
        print(f"Migrando contraseña para {username}: {password}")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", (hashed_password, username))
        print(f"Nueva contraseña hasheada: {hashed_password}")

conn.commit()
db.cerrar_conexion()
print("Migración de contraseñas completada")