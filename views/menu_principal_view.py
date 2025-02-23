import tkinter as tk
from tkinter import ttk, Menu
from services.database_service import DatabaseService

class MenuPrincipalView(tk.Tk):
    def __init__(self, controller, rol):
        super().__init__()
        self.controller = controller
        self.rol = rol
        self.db = DatabaseService()
        self.title("Clínica Dental")
        self.geometry("800x600")
        self._crear_menu()
    
    def _crear_menu(self):
        menu_bar = Menu(self)
        
        # Menú principal (para todos los roles)
        menu_principal = Menu(menu_bar, tearoff=0)
        menu_principal.add_command(label="Pacientes", command=self.controller.mostrar_pacientes)
        menu_principal.add_command(label="Visitas", command=self.controller.mostrar_visitas)
        menu_principal.add_command(label="Pagos", command=self.controller.mostrar_pagos)
        menu_principal.add_command(label="Citas", command=self.controller.mostrar_citas)
        menu_bar.add_cascade(label="Inicio", menu=menu_principal)
        
        # Menú solo para admin
        if self.rol == "admin":
            menu_admin = Menu(menu_bar, tearoff=0)
            menu_admin.add_command(label="Gestionar Usuarios", command=self.controller.mostrar_gestion_usuarios)
            menu_bar.add_cascade(label="Administración", menu=menu_admin)
        
        self.config(menu=menu_bar)