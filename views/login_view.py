# views/login_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService

class LoginView(tk.Tk):  # LoginView es la ventana raíz (tk.Tk)
    def __init__(self):
        super().__init__()  # No pasamos master, ya que es la raíz
        self.title("Login - Clínica Dental")
        self.geometry("300x200")
        self.resizable(False, False)
        self._crear_widgets()
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
        self.entry_usuario.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(self, text="Contraseña:").pack(pady=5)
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.pack(pady=5, fill=tk.X, padx=10)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15)
        
        ttk.Button(frame_botones, text="Iniciar Sesión", 
                  command=self._iniciar_sesion).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", 
                  command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _iniciar_sesion(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        
        if not usuario or not password:
            messagebox.showerror("Error", "Por favor, ingrese usuario y contraseña")
            return

        db = DatabaseService()
        rol = db.verificar_usuario(usuario, password)
        
        if rol:
            self.withdraw()  # Ocultar LoginView en lugar de destruirla
            print(f"Ocultando LoginView, raíz actual: {tk._default_root}")  # Depuración
            from controllers.main_controller import MainController
            from views.menu_principal_view import MenuPrincipalView
            main_controller = MainController(rol)
            # MenuPrincipalView se abrirá como Toplevel usando esta raíz
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")