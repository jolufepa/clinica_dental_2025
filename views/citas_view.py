# views/citas_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.cita import Cita
from views.nueva_cita_view import NuevaCitaView
from views.styles import configurar_estilos
class CitasView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id  # Almacenar el ID si se proporciona
        self.title("Gestión de Citas")
        self.geometry("1000x700")  # Aumentamos más el tamaño para asegurar visibilidad
        self._crear_widgets()
        configurar_estilos(self)  # Aplicar estilos globales
        self._cargar_pacientes()  # Cargar todos los pacientes al iniciar
        if paciente_id:
            self._cargar_citas()  # Cargar citas iniciales si hay un paciente_id
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)
    def _crear_widgets(self):
        # Frame superior con botones y buscador
        frame_superior = ttk.Frame(self)
        frame_superior.pack(pady=10, fill=tk.X)

        ttk.Button(frame_superior, text="Nueva Cita", 
                   command=self._nueva_cita).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_superior, text="Enviar Recordatorio", 
                   command=self._enviar_recordatorio).pack(side=tk.LEFT, padx=5)

        # Frame para el buscador de pacientes
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Buscar por ID del Paciente:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Buscar", command=self._buscar_paciente).pack(side=tk.LEFT, padx=5)

        # Treeview para mostrar pacientes
        self.tree_pacientes = ttk.Treeview(self, columns=("identificador", "nombre", "telefono"), show="headings")
        self.tree_pacientes.heading("identificador", text="Identificador")
        self.tree_pacientes.heading("nombre", text="Nombre")
        self.tree_pacientes.heading("telefono", text="Teléfono")
        for col in self.tree_pacientes["columns"]:
            self.tree_pacientes.column(col, width=120, anchor=tk.W)
        self.tree_pacientes.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Treeview para mostrar citas con nombres de columnas válidos
        self.tree_citas = ttk.Treeview(self, columns=("id_cita", "paciente", "fecha", "hora", "odontologo", "estado"), show="headings")
        self.tree_citas.heading("id_cita", text="ID Cita")
        self.tree_citas.heading("paciente", text="Paciente (ID)")
        self.tree_citas.heading("fecha", text="Fecha")
        self.tree_citas.heading("hora", text="Hora")
        self.tree_citas.heading("odontologo", text="Odontólogo")
        self.tree_citas.heading("estado", text="Estado")
        for col in self.tree_citas["columns"]:
            self.tree_citas.column(col, width=120, anchor=tk.W)
        self.tree_citas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

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
            print(f"Cargando citas para paciente_id: {self.paciente_id}")  # Depuración
            # Limpiar citas actuales
            for item in self.tree_citas.get_children():
                self.tree_citas.delete(item)

            if self.paciente_id:
                citas = self.controller.db.obtener_citas(self.paciente_id)
                print(f"Citas obtenidas: {citas}")  # Depuración
                # Insertar nuevas citas
                for cita in citas:
                    self.tree_citas.insert("", tk.END, values=(
                        cita.id_cita,
                        cita.identificador,
                        cita.fecha,
                        cita.hora,
                        cita.odontologo,
                        cita.estado
                    ))
            else:
                messagebox.showwarning("Advertencia", "Seleccione un paciente para cargar sus citas.")
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando citas: {str(e)}")

    def _nueva_cita(self):
        if self.paciente_id:
            from views.nueva_cita_view import NuevaCitaView
            NuevaCitaView(self.controller, self.paciente_id)
            self._cargar_citas()  # Actualizar la lista después de crear
        else:
            messagebox.showwarning("Advertencia", "Seleccione un paciente primero")

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
        if self.paciente_id:
            from views.nueva_cita_view import NuevaCitaView
            NuevaCitaView(self.controller, self.paciente_id)
            self._cargar_citas()  # Actualizar la lista después de crear
        else:
            messagebox.showwarning("Advertencia", "Seleccione un paciente primero")

    def _enviar_recordatorio(self):
        seleccion = self.tree_citas.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione una cita para enviar el recordatorio")
            return
        
        cita = self.tree_citas.item(seleccion, "values")
        cita_id = cita[0]  # ID de la cita (si lo usas)
        paciente_id = cita[1]  # Identificador del paciente
        try:
            paciente = self.controller.db.obtener_paciente(paciente_id)
            citas = self.controller.db.obtener_citas(paciente_id)
            cita_seleccionada = next((c for c in citas if c.id_cita == cita_id), None) or citas[0]  # Usar la primera si no hay coincidencia exacta
            if paciente and cita_seleccionada:
                self.controller.db.enviar_notificacion_cita(paciente.email, cita_seleccionada.fecha, cita_seleccionada.hora)
                messagebox.showinfo("Éxito", "Recordatorio enviado correctamente")
            else:
                messagebox.showerror("Error", "No se pudo encontrar el paciente o la cita")
        except Exception as e:
            messagebox.showerror("Error", f"Error al enviar recordatorio: {str(e)}")
    
    def _cerrar_ventana(self):
        if 'citas' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['citas']
        self.destroy()