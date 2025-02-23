# views/login_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService

class LoginView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = DatabaseService()  # Conexión persistente
        self.title("Login - Clínica Dental")
        self.geometry("300x200")
        self._crear_widgets()
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _crear_widgets(self):
        ttk.Label(self, text="Usuario:").pack(pady=5)
        self.entry_usuario = ttk.Entry(self)
        self.entry_usuario.pack(pady=5)

        ttk.Label(self, text="Contraseña:").pack(pady=5)
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        ttk.Button(self, text="Iniciar Sesión", command=self._intentar_login).pack(pady=10)

    def _intentar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        try:
            rol = self.db.verificar_usuario(usuario, password)
            if rol:
                self.destroy()
                from controllers.main_controller import MainController
                MainController(rol)
            else:
                messagebox.showerror("Error", "Credenciales inválidas")
        except Exception as e:
            messagebox.showerror("Error", f"Error de conexión: {str(e)}")