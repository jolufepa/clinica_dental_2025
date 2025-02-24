# controllers/main_controller.py
import tkinter as tk
from tkinter import ttk
from services.database_service import DatabaseService
from views.menu_principal_view import MenuPrincipalView
import sys
from pathlib import Path



# Añade la ruta del proyecto al sistema
sys.path.append(str(Path(__file__).resolve().parent.parent))

class MainController:
    def __init__(self, rol):
        self.rol = rol
        self.db = DatabaseService()  # Asegúrate de que esto use el Singleton
        self.vista_principal = None
        self._iniciar_aplicacion()
        self._ventanas_abiertas = {}
        print(f"Iniciando MainController, raíz actual: {tk._default_root}")  # Depuración

    def _iniciar_aplicacion(self):
        # Usar la raíz existente (LoginView como tk.Tk) para MenuPrincipalView
        self.vista_principal = MenuPrincipalView(self, self.rol)
        self._configurar_estilos()
        self._centrar_ventana()
        self.vista_principal.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)
        print(f"Iniciando aplicación, raíz actual: {tk._default_root}")  # Depuración

    def _configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use('clam')
        estilo.configure('TEntry', state='normal')
        estilo.configure('TButton', padding=6, font=('Arial', 10))
        estilo.configure('TEntry', font=('Arial', 10))
        estilo.configure('Treeview', font=('Arial', 10), rowheight=25)
        estilo.configure('Treeview.Heading', font=('Arial', 10, 'bold'))

    def _centrar_ventana(self):
        self.vista_principal.update_idletasks()
        ancho = self.vista_principal.winfo_width()
        alto = self.vista_principal.winfo_height()
        x = (self.vista_principal.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.vista_principal.winfo_screenheight() // 2) - (alto // 2)
        self.vista_principal.geometry(f'{ancho}x{alto}+{x}+{y}')
        
    def actualizar_lista_pagos(self):
        """Actualiza las vistas de pagos"""
        if 'pagos' in self._ventanas_abiertas:
            self._ventanas_abiertas['pagos']._cargar_pagos()
    # ================== MÉTODOS PRINCIPALES ==================
    def mostrar_pacientes(self):
        #"""Abre la gestión de pacientes"""
        self._abrir_ventana('pacientes', 'PacientesView')

    def mostrar_visitas(self, paciente_id=None):
        #"""Abre la gestión de visitas médicas"""
        self._abrir_ventana('visitas', 'VisitasView', paciente_id)

    def mostrar_pagos(self, paciente_id=None):
        #"""Abre la gestión de pagos"""
        self._abrir_ventana('pagos', 'PagosView', paciente_id)

    def mostrar_citas(self, paciente_id=None):
        #"""Abre la gestión de citas"""
        self._abrir_ventana('citas', 'CitasView', paciente_id)

    def mostrar_gestion_usuarios(self):
        #"""Abre la gestión de usuarios (solo admin)"""
        if self.rol == "admin":
            self._abrir_ventana('usuarios', 'GestionUsuariosView')

    # ================== MÉTODOS AUXILIARES ==================
    def _abrir_ventana(self, clave, nombre_vista, *args):
        if clave not in self._ventanas_abiertas or not self._ventanas_abiertas[clave].winfo_exists():
            modulo_nombre = nombre_vista.lower().replace('view', '_view')
            modulo = __import__(f'views.{modulo_nombre}', fromlist=[nombre_vista])
            clase_vista = getattr(modulo, nombre_vista)
            self._ventanas_abiertas[clave] = clase_vista(self, *args)  # Pasa *args correctamente
            self._ventanas_abiertas[clave].lift()  # Asegurar que la ventana esté al frente
            self._ventanas_abiertas[clave].focus_set()  # Asegurar que tenga el foco
            print(f"Abriendo {nombre_vista} con clave {clave}, raíz actual: {tk._default_root}")  # Depuración
        else:
            self._ventanas_abiertas[clave].lift()  # Levantar la ventana existente

    def _cerrar_aplicacion(self):
        DatabaseService().cerrar_conexion()  # Cierra solo aquí
        self.vista_principal.destroy()
    # En controllers/main_controller.py
    def actualizar_lista_pacientes(self):
        if 'pacientes' in self._ventanas_abiertas:
            ventana_pacientes = self._ventanas_abiertas['pacientes']
            ventana_pacientes._cargar_pacientes()  # Llama al método interno de la vista
            ventana_pacientes.update()

    def actualizar_lista_visitas(self):
        #"""Actualiza las vistas de visitas médicas"""
        if 'visitas' in self._ventanas_abiertas:
            self._ventanas_abiertas['visitas']._cargar_visitas()

    def actualizar_lista_citas(self):
        """Actualiza las vistas de citas"""
        if 'citas' in self._ventanas_abiertas and self._ventanas_abiertas['citas'].winfo_exists():
            self._ventanas_abiertas['citas']._cargar_citas()

    def actualizar_lista_usuarios(self):
        """Actualiza la vista de gestión de usuarios"""
        if 'usuarios' in self._ventanas_abiertas:
            self._ventanas_abiertas['usuarios']._cargar_usuarios()

    # ================== MÉTODOS DE DATOS ==================
    def obtener_pacientes(self):
        #"""Obtiene lista completa de pacientes"""
        return self.db.obtener_pacientes()

    def obtener_paciente(self, identificador):
        #"""Obtiene un paciente específico"""
        return self.db.obtener_paciente(identificador)

    def cerrar_sesion(self):
        #"""Cierra la sesión actual"""
        self._cerrar_aplicacion()
        from views.login_view import LoginView
        LoginView()
print(f"Chequeo de raíz global: {tk._default_root}")        
        