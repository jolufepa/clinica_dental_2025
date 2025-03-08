# ARCHIVO controllers/main_controller.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from views.menu_principal_view import MenuPrincipalView
import sys
from pathlib import Path
from views.styles import configurar_estilos


# Añade la ruta del proyecto al sistema
sys.path.append(str(Path(__file__).resolve().parent.parent))

class MainController:
    def __init__(self, rol, master=None):
        self.rol = rol
        self.master = master
        self.db = DatabaseService()
        self.vista_principal = None
        self._ventanas_abiertas = {}
        self._iniciar_aplicacion()
    def _iniciar_aplicacion(self):
        self.vista_principal = MenuPrincipalView(self, self.rol, master=self.master)
        configurar_estilos(self.vista_principal)
        self._centrar_ventana()
        self.vista_principal.protocol("WM_DELETE_WINDOW", self._cerrar_aplicacion)
        self.vista_principal.deiconify()

    def _centrar_ventana(self):
        self.vista_principal.update_idletasks()
        ancho = self.vista_principal.winfo_width()
        alto = self.vista_principal.winfo_height()
        x = (self.vista_principal.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.vista_principal.winfo_screenheight() // 2) - (alto // 2)
        self.vista_principal.geometry(f'{ancho}x{alto}+{x}+{y}')
    def mostrar_pacientes(self):
        """Abre la gestión de pacientes"""
        self._abrir_ventana('pacientes', 'PacientesView')

    def mostrar_visitas(self, paciente_id=None):
        self._abrir_ventana('visitas', 'VisitasView', paciente_id)

    def mostrar_pagos(self, paciente_id=None):
        self._abrir_ventana('pagos', 'PagosView', paciente_id)

    def mostrar_citas(self, paciente_id=None):
        self._abrir_ventana('citas', 'CitasView', paciente_id)

    def mostrar_gestion_usuarios(self):
        if self.rol == "admin":
            self._abrir_ventana('usuarios', 'GestionUsuariosView')
    def mostrar_informes(self):  # Nuevo método
        self._abrir_ventana('informes', 'InformesView')        
    def mostrar_presupuestos(self):  # Nuevo método
        self._abrir_ventana('presupuestos', 'PresupuestosView')  # Abrir vista de presupuestos
    def _abrir_ventana(self, clave, nombre_vista, *args):
        if clave not in self._ventanas_abiertas or not self._ventanas_abiertas[clave].winfo_exists():
            modulo_nombre = nombre_vista.lower().replace('view', '_view')
            modulo_mapeo = {
                'GestionUsuariosView': 'gestion_usuarios_view',
                'NuevoPacienteView': 'nuevo_paciente_view',
                'EditarPacienteView': 'editar_paciente_view',
                'NuevaCitaView': 'nueva_cita_view',
                'EditarCitaView': 'editar_cita_view',
                'NuevaVisitaView': 'nueva_visita_view',
                'EditarVisitaView': 'editar_visita_view',
                'NuevoPagoView': 'nuevo_pago_view',
                'EditarPagoView': 'editar_pago_view',
                'CitasView': 'citas_view',
                'PagosView': 'pagos_view',
                'VisitasView': 'visitas_view',
                'PresupuestosView': 'presupuestos_view',
                'InformesView': 'informes_view'  # Nuevo
            }
            if nombre_vista in modulo_mapeo:
                modulo_nombre = modulo_mapeo[nombre_vista]
            
            try:
                modulo = __import__(f'views.{modulo_nombre}', fromlist=[nombre_vista])
                clase_vista = getattr(modulo, nombre_vista)
                self._ventanas_abiertas[clave] = clase_vista(self, *args)
                configurar_estilos(self._ventanas_abiertas[clave])
            except ImportError as e:
                messagebox.showerror("Error", f"No se pudo cargar la vista: {str(e)}")
        else:
            self._ventanas_abiertas[clave].lift()

    def _cerrar_aplicacion(self):
        try:
            self.db.cerrar_conexion()
        except Exception as e:
            print(f"Error al cerrar la conexión: {str(e)}")
        if self.vista_principal:
            self.vista_principal.destroy()
        if self.master:
            self.master.withdraw()

    def actualizar_lista_pacientes(self):
        if 'pacientes' in self._ventanas_abiertas:
            ventana_pacientes = self._ventanas_abiertas['pacientes']
            ventana_pacientes._cargar_pacientes()
            ventana_pacientes.update()

    def actualizar_lista_visitas(self):
        if 'pacientes' in self._ventanas_abiertas and self._ventanas_abiertas['pacientes'].winfo_exists():
            self._ventanas_abiertas['pacientes']._cargar_visitas()

    def actualizar_lista_citas(self):
        if 'pacientes' in self._ventanas_abiertas and self._ventanas_abiertas['pacientes'].winfo_exists():
            self._ventanas_abiertas['pacientes']._cargar_citas()

    def actualizar_lista_usuarios(self):
        if 'usuarios' in self._ventanas_abiertas:
            self._ventanas_abiertas['usuarios']._cargar_usuarios()

    def actualizar_lista_pagos(self):
        if 'pacientes' in self._ventanas_abiertas and self._ventanas_abiertas['pacientes'].winfo_exists():
            self._ventanas_abiertas['pacientes']._cargar_pagos()

    def obtener_pacientes(self):
        return self.db.obtener_pacientes()

    def obtener_paciente(self, identificador):
        return self.db.obtener_paciente(identificador)

    def obtener_visitas(self, paciente_id):
        return self.db.obtener_visitas_paciente(paciente_id)
    
    def cerrar_sesion(self):
        # Cerrar todas las ventanas abiertas
        for clave, ventana in list(self._ventanas_abiertas.items()):
            if ventana.winfo_exists():
                ventana.destroy()
        self._ventanas_abiertas.clear()

        # Cerrar la ventana principal
        if self.vista_principal and self.vista_principal.winfo_exists():
            self.vista_principal.destroy()
            self.vista_principal = None

        # Cerrar la conexión a la base de datos
        try:
            self.db.cerrar_conexion()
        except Exception as e:
            print(f"Error al cerrar la conexión: {str(e)}")

        if self.master:
            self.master.withdraw()
    
        