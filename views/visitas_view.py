# views/visitas_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService

class VisitasView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id  # Almacenar el ID si se proporciona
        self.title("Gestión de Visitas")
        self.geometry("1000x600")
        self._crear_widgets()
        self._cargar_pacientes()  # Cargar todos los pacientes al iniciar
        if paciente_id:
            self._cargar_visitas()  # Cargar visitas iniciales si hay un paciente_id

    def _crear_widgets(self):
        # Frame principal para organizar los widgets
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

        # Treeview para mostrar visitas
        self.tree_visitas = ttk.Treeview(main_frame, columns=("ID Visita", "Fecha", "Motivo", "Estado"), show="headings")
        self.tree_visitas.heading("ID Visita", text="ID Visita")
        self.tree_visitas.heading("Fecha", text="Fecha")
        self.tree_visitas.heading("Motivo", text="Motivo")
        self.tree_visitas.heading("Estado", text="Estado")
        self.tree_visitas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para crear nueva visita
        btn_nueva_visita = ttk.Button(
            self, 
            text="Nueva Visita", 
            command=self._abrir_nueva_visita
        )
        btn_nueva_visita.pack(pady=10)

        # Vincular la selección en el Treeview de pacientes para actualizar visitas
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

    def _cargar_visitas(self):
        """Obtiene y muestra las visitas del paciente seleccionado desde la base de datos"""
        try:
            # Limpiar visitas actuales
            for item in self.tree_visitas.get_children():
                self.tree_visitas.delete(item)

            if self.paciente_id:
                visitas = self.controller.db.obtener_visitas(self.paciente_id)
                # Insertar nuevas visitas
                for visita in visitas:
                    self.tree_visitas.insert("", tk.END, values=(
                        visita.id_visita,
                        visita.fecha,
                        visita.motivo,
                        visita.estado
                    ))
            else:
                print("No se seleccionó un paciente, no se cargan visitas.")
        except Exception as e:
            print(f"Error al cargar visitas: {str(e)}")

    def _on_paciente_select(self, event):
        """Actualiza las visitas cuando se selecciona un paciente en el Treeview"""
        seleccion = self.tree_pacientes.selection()
        if seleccion:
            self.paciente_id = self.tree_pacientes.item(seleccion, "values")[0]  # Obtener ID del paciente
            self._cargar_visitas()  # Cargar visitas del paciente seleccionado
        else:
            self.paciente_id = None
            self._cargar_visitas()  # Limpiar visitas si no hay selección

    def _abrir_nueva_visita(self):
        """Abre la ventana de nueva visita con el paciente seleccionado"""
        seleccion = self.tree_pacientes.selection()
        if seleccion:
            paciente_id = self.tree_pacientes.item(seleccion, "values")[0]  # Obtener ID
            from views.nueva_visita_view import NuevaVisitaView
            NuevaVisitaView(self.controller, paciente_id)
        else:
            messagebox.showwarning("Error", "Seleccione un paciente primero")

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