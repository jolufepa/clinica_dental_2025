# views/menu_principal_view.py
import tkinter as tk
from tkinter import ttk, messagebox

class MenuPrincipalView(tk.Toplevel):
    def __init__(self, controller, rol):
        # Usar la raíz existente (LoginView como tk.Tk) en lugar de crear una implícita
        super().__init__(tk._default_root or None)  # Usar la raíz activa o None si no hay
        self.controller = controller
        self.rol = rol
        self.title("Menú Principal - Clínica Dental")
        self.geometry("600x500")  # Ajustamos el tamaño para mayor visibilidad
        self.resizable(False, False)
        self._crear_widgets()
        self._centrar_ventana()
        self.focus_set()  # Asegurar que esta ventana tenga el foco
        print(f"Abriendo MenuPrincipalView, raíz actual: {tk._default_root}")  # Depuración

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Botones para las funcionalidades principales
        ttk.Button(main_frame, text="Gestión de Pacientes", 
                  command=self.controller.mostrar_pacientes).pack(pady=5, fill=tk.X)
        
        ttk.Button(main_frame, text="Gestión de Visitas", 
                  command=self.controller.mostrar_visitas).pack(pady=5, fill=tk.X)
        
        ttk.Button(main_frame, text="Gestión de Pagos", 
                  command=self.controller.mostrar_pagos).pack(pady=5, fill=tk.X)
        
        ttk.Button(main_frame, text="Gestión de Citas", 
                  command=self.controller.mostrar_citas).pack(pady=5, fill=tk.X)

        if self.rol == "admin":
            ttk.Button(main_frame, text="Gestión de Usuarios", 
                      command=self.controller.mostrar_gestion_usuarios).pack(pady=5, fill=tk.X)

        ttk.Button(main_frame, text="Cerrar Sesión", 
                  command=self.controller.cerrar_sesion).pack(pady=20, fill=tk.X)

    def _cerrar_ventana(self):
        self.destroy()