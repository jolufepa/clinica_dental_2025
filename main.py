# main.py - Punto de entrada principal de la aplicación
import tkinter as tk  # Importar tkinter al inicio
from views.login_view import LoginView

def inicializar_usuarios_base():
    """Crea usuarios iniciales si no existen (solo para desarrollo)"""
    from services.database_service import DatabaseService
    db = DatabaseService()
    
    # Usuarios de prueba
    usuarios_iniciales = [
        ("admin1", "admin123", "admin"),
        ("recepcion1", "recepcion123", "recepcion")
    ]
    
    try:
        for username, password, role in usuarios_iniciales:
            if not db.verificar_usuario(username, password):
                db.crear_usuario(username, password, role)
    except Exception as e:
        print(f"Error inicializando usuarios: {str(e)}")

if __name__ == "__main__":
    # Crear usuarios iniciales (solo en primera ejecución)
    inicializar_usuarios_base()
    
    # Iniciar directamente con LoginView como ventana raíz (tk.Tk)
    login_window = LoginView()  # LoginView es tk.Tk, no necesita master
    login_window.focus_set()  # Asegurar que LoginView tenga el foco
    
    # Depuración para verificar la raíz
    print(f"Raíz inicial: {tk._default_root}")
    
    try:
        login_window.mainloop()  # Usar mainloop de LoginView como raíz
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        