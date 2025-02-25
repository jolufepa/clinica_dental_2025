# views/login_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from views.styles import configurar_estilos

class LoginView(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master=master)  # Usar el master proporcionado por MainController
        self.title("Inicio de Sesión")
        self.geometry("400x300")
        self._crear_widgets()
        configurar_estilos(self)  # Aplicar estilos globales
        self.protocol("WM_DELETE_WINDOW", self._on_close)  # Manejar cierre de la ventana
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_widgets(self):
        ttk.Label(self, text="Usuario:").pack(pady=5)
        self.entry_usuario = ttk.Entry(self)
        self.entry_usuario.pack(pady=5)

        ttk.Label(self, text="Contraseña:").pack(pady=5)
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        ttk.Button(self, text="Iniciar Sesión", command=self._iniciar_sesion).pack(pady=10)

    def _iniciar_sesion(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        db = DatabaseService()
        rol = db.verificar_usuario(usuario, password)
        if rol:
            from controllers.main_controller import MainController
            # Crear MainController y pasar la referencia a LoginView
            self.controller = MainController(rol, master=self.master)
            self.controller.login_view = self  # Informar a MainController que este es el LoginView
            self.withdraw()  # Ocultar login al iniciar sesión
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

    def _on_close(self):
        # Ocultar en lugar de destruir para que MainController pueda manejarla
        self.withdraw()