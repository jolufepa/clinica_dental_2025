import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.visita import Visita
from views.nueva_visita_view import NuevaVisitaView
from views.styles import configurar_estilos
from views.tooltip import ToolTip  # Importar la clase ToolTip

class VisitasView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id  # Almacenar el ID si se proporciona
        self.title("Gestión de Visitas del Paciente")
        self.geometry("600x400")  # Reducimos el tamaño ya que solo mostramos visitas
        self.resizable(True, True)  # Mantener redimensionable
        self._crear_widgets()
        if paciente_id:
            self._cargar_visitas_directo()  # Cargar visitas directamente si hay paciente_id
        else:
            self._cargar_pacientes_y_visitas()  # Cargar todos los pacientes y permitir búsqueda
        configurar_estilos(self)  # Aplicar estilos globales
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)

    def _crear_widgets(self):
        # Frame principal para organizar los widgets
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if not self.paciente_id:  # Solo mostrar buscador y Treeview de pacientes si no hay paciente_id
            # Frame para el buscador
            search_frame = ttk.Frame(main_frame)
            search_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(search_frame, text="Buscar por ID del Paciente:").pack(side=tk.LEFT, padx=5)
            self.search_entry = ttk.Entry(search_frame)
            self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            buscar_btn = ttk.Button(search_frame, text="Buscar", command=self._buscar_paciente)
            buscar_btn.pack(side=tk.LEFT, padx=5)
            ToolTip(buscar_btn, "Busca un paciente por su identificador para ver sus visitas")  # Añadir tooltip

            # Treeview para mostrar pacientes
            self.tree_pacientes = ttk.Treeview(main_frame, columns=("identificador", "nombre", "telefono"), show="headings")
            self.tree_pacientes.heading("identificador", text="Identificador")
            self.tree_pacientes.heading("nombre", text="Nombre")
            self.tree_pacientes.heading("telefono", text="Teléfono")
            for col in self.tree_pacientes["columns"]:
                self.tree_pacientes.column(col, width=150, anchor=tk.W)
            self.tree_pacientes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Vincular la selección en el Treeview de pacientes para actualizar visitas
            self.tree_pacientes.bind("<<TreeviewSelect>>", self._on_paciente_select)

        # Treeview para mostrar visitas (siempre visible, pero vacío si no hay paciente_id)
        self.tree_visitas = ttk.Treeview(main_frame, columns=("id_visita", "identificador", "fecha", "motivo", "diagnostico", "tratamiento", "odontologo", "estado"), show="headings")
        self.tree_visitas.heading("id_visita", text="ID Visita")
        self.tree_visitas.heading("identificador", text="Paciente (ID)")
        self.tree_visitas.heading("fecha", text="Fecha")
        self.tree_visitas.heading("motivo", text="Motivo")
        self.tree_visitas.heading("diagnostico", text="Diagnóstico")
        self.tree_visitas.heading("tratamiento", text="Tratamiento")
        self.tree_visitas.heading("odontologo", text="Odontólogo")
        self.tree_visitas.heading("estado", text="Estado")
        for col in self.tree_visitas["columns"]:
            self.tree_visitas.column(col, width=120 if col in ["id_visita", "estado"] else 150, anchor=tk.W)
        self.tree_visitas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Frame para el botón "Nueva Visita" (siempre visible, pero deshabilitado si no hay paciente_id)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        self.nuevo_visita_btn = ttk.Button(btn_frame, text="Nueva Visita", command=self._abrir_nueva_visita)
        self.nuevo_visita_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(self.nuevo_visita_btn, "Crea una nueva visita para el paciente seleccionado")  # Añadir tooltip
        if not self.paciente_id:
            self.nuevo_visita_btn.config(state="disabled")  # Deshabilitar si no hay paciente_id

    def _cargar_pacientes(self):
        """Obtiene y muestra todos los pacientes desde la base de datos (solo si no hay paciente_id)"""
        if not hasattr(self, 'tree_pacientes') or not self.tree_pacientes:
            return  # No cargar si no existe el Treeview de pacientes
        try:
            pacientes = self.controller.db.obtener_pacientes()
            print(f"Pacientes obtenidos: {pacientes}")  # Depuración
            # Limpiar datos antiguos
            for item in self.tree_pacientes.get_children():
                self.tree_pacientes.delete(item)
            # Insertar nuevos datos
            for paciente in pacientes:
                self.tree_pacientes.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pacientes: {str(e)}")

    def _cargar_visitas(self):
        """Obtiene y muestra las visitas del paciente seleccionado desde la base de datos (manual o automático)"""
        try:
            print(f"Cargando visitas para paciente_id: {self.paciente_id}")  # Depuración
            # Limpiar visitas actuales
            for item in self.tree_visitas.get_children():
                self.tree_visitas.delete(item)

            if self.paciente_id:
                visitas = self.controller.db.obtener_visitas(self.paciente_id)
                print(f"Visitas obtenidas: {visitas}")  # Depuración
                print(f"Visitas detalladas: {[v.__dict__ for v in visitas]}")  # Depuración detallada
                # Insertar nuevas visitas con el orden correcto de los campos
                for visita in visitas:
                    self.tree_visitas.insert("", tk.END, values=(
                        visita.id_visita,
                        visita.identificador,
                        visita.fecha,
                        visita.motivo,
                        visita.diagnostico,
                        visita.tratamiento,
                        visita.odontologo,
                        visita.estado
                    ))
            else:
                messagebox.showwarning("Advertencia", "Seleccione un paciente para cargar sus visitas.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar visitas: {str(e)}")

    def _on_paciente_select(self, event):
        """Actualiza las visitas cuando se selecciona un paciente en el Treeview (solo si no hay paciente_id inicial)"""
        if not hasattr(self, 'tree_pacientes') or not self.tree_pacientes:
            return  # No hacer nada si no existe el Treeview de pacientes
        seleccion = self.tree_pacientes.selection()
        if seleccion:
            self.paciente_id = self.tree_pacientes.item(seleccion, "values")[0]  # Obtener ID del paciente
            self._cargar_visitas()  # Cargar visitas del paciente seleccionado
        else:
            self.paciente_id = None
            self._cargar_visitas()  # Limpiar visitas si no hay selección

    def _abrir_nueva_visita(self):
        """Abre la ventana de nueva visita con el paciente seleccionado o el paciente_id actual"""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Seleccione un paciente primero")
            return
        from views.nueva_visita_view import NuevaVisitaView
        NuevaVisitaView(self.controller, self.paciente_id)
        self._cargar_visitas()  # Actualizar la lista después de crear

    def _buscar_paciente(self):
        """Busca un paciente por su ID y muestra solo ese paciente en el Treeview (solo si no hay paciente_id inicial)"""
        if self.paciente_id:
            messagebox.showwarning("Advertencia", "Ya se está gestionando un paciente específico. Use 'Nueva Visita' para añadir visitas.")
            return
        id_buscado = self.search_entry.get().strip()
        if not id_buscado:
            messagebox.showwarning("Advertencia", "Ingrese un ID de paciente para buscar")
            return

        try:
            print(f"Buscando paciente con ID: {id_buscado}")  # Depuración
            # Obtener el paciente desde la base de datos
            paciente = self.controller.db.obtener_paciente(id_buscado)
            if paciente:
                print(f"Paciente encontrado: {paciente.__dict__}")  # Depuración
                # Limpiar el Treeview de pacientes
                for item in self.tree_pacientes.get_children():
                    self.tree_pacientes.delete(item)
                # Insertar solo el paciente encontrado
                self.tree_pacientes.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono
                ))
                # Actualizar el paciente_id y cargar sus visitas
                self.paciente_id = paciente.identificador
                self._cargar_visitas()
            else:
                messagebox.showerror("Error", "No se encontró un paciente con ese ID")
                # Limpiar el Treeview de pacientes
                for item in self.tree_pacientes.get_children():
                    self.tree_pacientes.delete(item)
                self.paciente_id = None
                self._cargar_visitas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar paciente: {str(e)}")

    def _cerrar_ventana(self):
        if 'visitas' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['visitas']
        self.destroy()

    def _cargar_visitas_directo(self):
        """Carga directamente las visitas del paciente especificado, sin mostrar la lista de pacientes."""
        try:
            print(f"Cargando visitas directamente para paciente_id: {self.paciente_id}")
            # Limpiar visitas actuales
            for item in self.tree_visitas.get_children():
                self.tree_visitas.delete(item)
            
            if self.paciente_id:
                visitas = self.controller.db.obtener_visitas(self.paciente_id)
                # Insertar nuevas visitas con el orden correcto de los campos
                for visita in visitas:
                    self.tree_visitas.insert("", tk.END, values=(
                        visita.id_visita,
                        visita.identificador,
                        visita.fecha,
                        visita.motivo,
                        visita.diagnostico,
                        visita.tratamiento,
                        visita.odontologo,
                        visita.estado
                    ))
            else:
                messagebox.showwarning("Advertencia", "No se especificó un paciente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar visitas directamente: {str(e)}")

    def _cargar_pacientes_y_visitas(self):
        """Carga todos los pacientes y permite buscar/cargar visitas manualmente."""
        self._cargar_pacientes()
        self._cargar_visitas()  # Cargar visitas vacías o del último paciente seleccionado