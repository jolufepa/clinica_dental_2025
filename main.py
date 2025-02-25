# main.py
import tkinter as tk
from controllers.main_controller import MainController

def main():
    # Simulamos un login directo con rol "recepcion" para desarrollo (o "admin" si prefieres)
    rol = "admin"  # Cambia a "admin" o el rol que desees para pruebas
    root = tk.Tk()  # Crear la raíz manualmente
    root.withdraw()  # Ocultar la raíz temporalmente
    main_controller = MainController(rol, master=root)  # Abrir MenuPrincipalView directamente
    root.mainloop()

if __name__ == "__main__":
    main()













"""""""""# main.py
import tkinter as tk
from views.login_view import LoginView

def inicializar_usuarios_base():
    from services.database_service import DatabaseService
    db = DatabaseService()
    usuarios_iniciales = [
        ("admin1", "admin123", "admin"),
        ("recepcion1", "recepcion123", "recepción")
    ]
    try:
        for username, password, role in usuarios_iniciales:
            # Verificar si el usuario existe usando el username (ignora la contraseña por ahora)
            self.cursor.execute("SELECT username FROM usuarios WHERE username = ?", (username,))
            if not self.cursor.fetchone():
                # Si no existe, crear el usuario con la contraseña hasheada
                db.crear_usuario(username, password, role)
        db.conn.commit()  # Asegurar que los cambios se guarden
    except Exception as e:
        print(f"Error inicializando usuarios: {str(e)}")
        raise

if __name__ == "__main__":
    inicializar_usuarios_base()
    login_window = LoginView()
    login_window.mainloop()"""""
        