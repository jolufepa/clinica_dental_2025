# views/menu_principal_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from views.styles import configurar_estilos

class MenuPrincipalView(tk.Toplevel):
    def __init__(self, controller, rol, master=None):
        super().__init__(master=master)  # Usar la raíz proporcionada por MainController si existe
        self.controller = controller
        self.rol = rol
        self.title("Menú Principal")
        self.geometry("600x400")
        self._crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        configurar_estilos(self)  # Aplicar estilos globales
    
    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def _crear_widgets(self):
        # Botones para las funcionalidades principales
        ttk.Button(self, text="Gestión de Pacientes", 
                  command=self.controller.mostrar_pacientes).pack(pady=5, fill=tk.X)
        
        ttk.Button(self, text="Gestión de Visitas", 
                  command=self.controller.mostrar_visitas).pack(pady=5, fill=tk.X)
        
        ttk.Button(self, text="Gestión de Pagos", 
                  command=self.controller.mostrar_pagos).pack(pady=5, fill=tk.X)
        
        ttk.Button(self, text="Gestión de Citas", 
                  command=self.controller.mostrar_citas).pack(pady=5, fill=tk.X)

        if self.rol == "admin":
            ttk.Button(self, text="Gestión de Usuarios", 
                      command=self.controller.mostrar_gestion_usuarios).pack(pady=5, fill=tk.X)

        ttk.Button(self, text="Cerrar Sesión", 
                  command=self.controller.cerrar_sesion).pack(pady=20, fill=tk.X)
    
    def _on_close(self):
        self.controller.cerrar_sesion()  # Delegar el cierre de sesión al controlador
        self.destroy()  # Cerrar esta ventana completamente