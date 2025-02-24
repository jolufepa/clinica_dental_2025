# views/citas_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.cita import Cita

class CitasView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id  # Almacenar el ID si se proporciona
        self.title("Gestión de Citas")
        self.geometry("1000x700")  # Aumentamos más el tamaño para asegurar visibilidad
        self._crear_widgets()
        self._cargar_pacientes()  # Cargar pacientes al iniciar
        if paciente_id:
            self._cargar_citas()  # Cargar citas iniciales si hay un paciente_id

    def _crear_widgets(self):
        # Frame principal para organizar los Treeviews
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para el buscador
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Buscar por ID del Paciente:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Buscar", command=self._buscar_paciente).pack(side=tk.LEFT, padx=5)

        # Treeview para mostrar pacientes
        self.tree_pacientes = ttk.Treeview(main_frame, columns=("ID", "Nombre", "Teléfono"), show="headings")
        self.tree_pacientes.heading("ID", text="Identificador")
        self.tree_pacientes.heading("Nombre", text="Nombre")
        self.tree_pacientes.heading("Teléfono", text="Teléfono")
        self.tree_pacientes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview para mostrar citas
        self.tree_citas = ttk.Treeview(main_frame, columns=("ID", "Fecha", "Hora", "Odontólogo", "Estado"), show="headings")
        for col in ("ID", "Fecha", "Hora", "Odontólogo", "Estado"):
            self.tree_citas.heading(col, text=col)  # Usar col directamente como texto
            self.tree_citas.column(col, width=120, anchor=tk.CENTER)
        self.tree_citas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para crear nueva cita (restaurado y posicionado claramente)
        btn_nueva_cita = ttk.Button(
            self, 
            text="Nueva Cita", 
            command=self._nueva_cita
        )
        btn_nueva_cita.pack(pady=20, anchor=tk.CENTER)  # Aumentamos pady y usamos anchor para centrar

        # Vincular la selección en el Treeview de pacientes para actualizar citas
        self.tree_pacientes.bind("<<TreeviewSelect>>", self._on_paciente_select)

    def _cargar_pacientes(self):
        """Obtiene y muestra todos los pacientes desde la base de datos"""
        try:
            pacientes = self.controller.db.obtener_pacientes()
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
            print(f"Error al cargar pacientes: {str(e)}")

    def _cargar_citas(self):
        """Obtiene y muestra las citas del paciente seleccionado desde la base de datos"""
        try:
            # Limpiar citas actuales
            for item in self.tree_citas.get_children():
                self.tree_citas.delete(item)

            if self.paciente_id:
                citas = self.controller.db.obtener_citas(self.paciente_id)
                # Insertar nuevas citas
                for cita in citas:
                    self.tree_citas.insert("", tk.END, values=(
                        cita.id_cita,
                        cita.fecha,
                        cita.hora,
                        cita.odontologo,
                        cita.estado.capitalize()
                    ))
            else:
                print("No se seleccionó un paciente, no se cargan citas.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar citas: {str(e)}")

    def _on_paciente_select(self, event):
        """Actualiza las citas cuando se selecciona un paciente en el Treeview"""
        seleccion = self.tree_pacientes.selection()
        if seleccion:
            self.paciente_id = self.tree_pacientes.item(seleccion, "values")[0]  # Obtener ID del paciente
            self._cargar_citas()  # Cargar citas del paciente seleccionado
        else:
            self.paciente_id = None
            self._cargar_citas()  # Limpiar citas si no hay selección

    def _buscar_paciente(self):
        """Busca un paciente por su ID y muestra solo ese paciente en el Treeview"""
        id_buscado = self.search_entry.get().strip()
        if not id_buscado:
            messagebox.showwarning("Advertencia", "Ingrese un ID de paciente para buscar")
            return

        try:
            # Obtener el paciente desde la base de datos
            paciente = self.controller.db.obtener_paciente(id_buscado)
            if paciente:
                # Limpiar el Treeview de pacientes
                for item in self.tree_pacientes.get_children():
                    self.tree_pacientes.delete(item)
                # Insertar solo el paciente encontrado
                self.tree_pacientes.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono
                ))
                # Actualizar el paciente_id y cargar sus citas
                self.paciente_id = paciente.identificador
                self._cargar_citas()
            else:
                messagebox.showerror("Error", "No se encontró un paciente con ese ID")
                # Limpiar el Treeview de pacientes
                for item in self.tree_pacientes.get_children():
                    self.tree_pacientes.delete(item)
                self.paciente_id = None
                self._cargar_citas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar paciente: {str(e)}")

    def _nueva_cita(self):
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Seleccione un paciente primero")
            return
        print(f"Abriendo NuevaCitaView con paciente_id: {self.paciente_id}")  # Depuración
        from .nueva_cita_view import NuevaCitaView
        self.grab_release()  # <--- Liberar el grab antes de abrir NuevaCitaView
        nueva_cita_window = NuevaCitaView(self.controller, self.paciente_id)
        nueva_cita_window.lift()
        nueva_cita_window.focus_set()