# ARCHIVO views/paciente_view.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from models.pago import Pago
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.paciente import Paciente
from models.cita import Cita
from models.visita import Visita
from models.pago import Pago
from datetime import datetime
from views.styles import configurar_estilos
from models.cita import Cita
class PacientesView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Gestión de Pacientes Clinica P&D ")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.paciente_id = None
        self.personal_vars = {}
        self.personal_widgets = {}
        self.historial_widgets = {}
        self._crear_widgets()
        self._centrar_ventana()
        configurar_estilos(self)
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Buscar Paciente:").pack(side=tk.LEFT, padx=5)

        # Usamos ttk.Combobox con autocompletado
        self.search_combo = ttk.Combobox(search_frame, width=30, postcommand=self._actualizar_sugerencias)
        self.search_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_combo.bind('<KeyRelease>', self._actualizar_sugerencias)  # Actualiza sugerencias al escribir
        self.search_combo.bind('<Return>', lambda event: self._buscar_paciente())  # Busca al presionar Enter
        self.search_combo.bind('<<ComboboxSelected>>', self._on_sugerencia_seleccionada)  # Captura selección

        ttk.Button(search_frame, text="Buscar", command=self._buscar_paciente).pack(side=tk.LEFT, padx=5)

        # Resto del código (button_frame, notebook, etc.) permanece igual
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Agregar Paciente", command=self._abrir_nuevo_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self._abrir_editar_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self._eliminar_paciente).pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        personal_frame = ttk.Frame(self.notebook)
        self.notebook.add(personal_frame, text="Información Personal")
        self._crear_formulario_personal(personal_frame)

        historial_frame = ttk.Frame(self.notebook)
        self.notebook.add(historial_frame, text="Historial Médico")
        self._crear_formulario_historial(historial_frame)

        citas_frame = ttk.Frame(self.notebook)
        self.notebook.add(citas_frame, text="Citas")
        self._crear_lista_citas(citas_frame)

        visitas_frame = ttk.Frame(self.notebook)
        self.notebook.add(visitas_frame, text="Visitas")
        self._crear_lista_visitas(visitas_frame)

        pagos_frame = ttk.Frame(self.notebook)
        self.notebook.add(pagos_frame, text="Pagos y Deudas")
        self._crear_lista_pagos(pagos_frame)

    def _crear_formulario_personal(self, frame):
        fields = [
            ("DNI/NIF/NIE", 20),
            ("Nombre", 30),
            ("Fecha Nacimiento", 15),
            ("Teléfono", 15),
            ("Email", 30),
            ("Dirección", 40)
        ]
        self.personal_widgets = {}
        print(f"Inicializando self.personal_vars: {self.personal_vars}")  # Depuración
        for i, (label_text, width) in enumerate(fields):
            ttk.Label(frame, text=label_text + ":").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            var = tk.StringVar()
            key = {
                "DNI/NIF/NIE": "identificador",
                "Nombre": "nombre",
                "Fecha Nacimiento": "fecha_nacimiento",
                "Teléfono": "telefono",
                "Email": "email",
                "Dirección": "direccion"
            }[label_text]
            self.personal_vars[key] = var
            print(f"Asignando clave {key} a self.personal_vars")  # Depuración
            entry = ttk.Entry(frame, textvariable=var, width=width, state="disabled")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.personal_widgets[key] = entry
            print(f"Creando widget ttk.Entry para {key}")

    def _crear_formulario_historial(self, frame):
        fields = [
            ("Historial", 50),
            ("Alergias", 50),
            ("Tratamientos Previos", 50),
            ("Notas", 50)
        ]
        self.historial_widgets = {}
        for i, (label_text, width) in enumerate(fields):
            ttk.Label(frame, text=label_text + ":").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            text = tk.Text(frame, height=3, width=width, state="disabled")
            text.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            key = label_text.lower().replace(' ', '_')
            self.historial_widgets[key] = text
            print(f"Creando widget tk.Text para {key}")

    def _crear_lista_citas(self, frame):
        # Frame para botones
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Gestionar Citas", command=lambda: self._abrir_citas_view()).pack(side=tk.LEFT, padx=5)

        # Treeview para listar citas
        self.tree_citas = ttk.Treeview(frame, columns=("ID", "Fecha", "Hora", "Odontólogo", "Estado"), show="headings", height=5)
        for col in self.tree_citas["columns"]:
            self.tree_citas.heading(col, text=col)
            self.tree_citas.column(col, width=120, anchor=tk.W, stretch=tk.YES)
        self.tree_citas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Vincular eventos: selección y doble clic para edición
        self.tree_citas.bind("<<TreeviewSelect>>", self._on_cita_select)
        self.tree_citas.bind("<Double-1>", self._editar_cita)  # Añadir edición con doble clic

    def _crear_lista_visitas(self, frame):
        # Frame para el botón
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Gestionar Visitas", command=lambda: self._abrir_visitas_view()).pack(side=tk.LEFT, padx=5)

        # Treeview para mostrar visitas
        self.tree_visitas = ttk.Treeview(frame, columns=("ID", "Fecha", "Motivo", "Diagnóstico", "Odontólogo", "Estado"), show="headings", height=5)
        for col in self.tree_visitas["columns"]:
            self.tree_visitas.heading(col, text=col)
            self.tree_visitas.column(col, width=120, anchor=tk.W, stretch=tk.YES)
        self.tree_visitas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Vincular eventos: selección y doble clic para edición
        self.tree_visitas.bind("<<TreeviewSelect>>", self._on_visita_select)
        self.tree_visitas.bind("<Double-1>", self._editar_visita)  # Añadir edición con doble clic

    def _editar_visita(self, event):
        """Abre un diálogo para editar la visita seleccionada en el Treeview."""
        selected_item = self.tree_visitas.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona una visita primero")
            return

        values = self.tree_visitas.item(selected_item[0])['values']
        if not values or len(values) < 6:
            messagebox.showerror("Error", "Datos de visita inválidos")
            return

        id_visita, fecha, motivo, diagnostico, odontologo, estado = values

        # Crear una ventana de edición
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Editar Visita ID: {id_visita}")
        edit_window.geometry("400x400")
        edit_window.transient(self)
        edit_window.grab_set()

        # Campos de edición
        ttk.Label(edit_window, text="Fecha (YYYY-MM-DD):").pack(pady=5)
        fecha_var = tk.StringVar(value=fecha)
        ttk.Entry(edit_window, textvariable=fecha_var).pack(pady=5)

        ttk.Label(edit_window, text="Motivo:").pack(pady=5)
        motivo_var = tk.StringVar(value=motivo)
        ttk.Entry(edit_window, textvariable=motivo_var).pack(pady=5)

        ttk.Label(edit_window, text="Diagnóstico:").pack(pady=5)
        diagnostico_var = tk.StringVar(value=diagnostico)
        ttk.Entry(edit_window, textvariable=diagnostico_var).pack(pady=5)

        ttk.Label(edit_window, text="Odontólogo:").pack(pady=5)
        odontologo_var = tk.StringVar(value=odontologo)
        ttk.Entry(edit_window, textvariable=odontologo_var).pack(pady=5)

        ttk.Label(edit_window, text="Estado:").pack(pady=5)
        estado_var = tk.StringVar(value=estado)
        ttk.Combobox(edit_window, textvariable=estado_var, values=["Pendiente", "Completada", "Cancelada"]).pack(pady=5)

  
    def _crear_lista_pagos(self, frame):
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Gestionar Pagos", command=lambda: self._abrir_pagos_view()).pack(side=tk.LEFT, padx=5)

        self.tree_pagos = ttk.Treeview(frame, columns=("ID", "Fecha", "Monto Total", "Pagado", "Método", "Saldo"), show="headings", height=5)
        for col in self.tree_pagos["columns"]:
            self.tree_pagos.heading(col, text=col)
            self.tree_pagos.column(col, width=120, anchor=tk.W, stretch=tk.YES)
        self.tree_pagos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_pagos.bind("<<TreeviewSelect>>", self._on_pago_select)

    def _buscar_paciente(self):
        texto_busqueda = self.search_combo.get().strip()
        try:
            # Si el texto incluye " - ", extraer solo el identificador
            if " - " in texto_busqueda:
                identificador = texto_busqueda.split(" - ")[0]
            else:
                identificador = texto_busqueda.upper()

            print(f"Buscando paciente con identificador: {identificador}")
            paciente = self.controller.db.obtener_paciente(identificador)  # Usamos obtener_paciente para buscar por identificador exacto
            if paciente:
                print(f"Paciente encontrado: Identificador={getattr(paciente, 'identificador', 'No disponible')}, "
                    f"Nombre={getattr(paciente, 'nombre', 'No disponible')}, "
                    f"Teléfono={getattr(paciente, 'telefono', 'No disponible')}")
                self.paciente_id = getattr(paciente, 'identificador', None)
                if self.paciente_id:
                    self._cargar_datos_paciente(paciente)
                    self._cargar_citas()
                    self._cargar_visitas()
                    self._cargar_pagos()
                    messagebox.showinfo("Éxito", f"Paciente encontrado: {getattr(paciente, 'nombre', 'Desconocido')}")
                else:
                    raise AttributeError("El paciente no tiene un identificador válido")
            else:
                messagebox.showerror("Error", "No se encontró un paciente con ese ID, Nombre o Teléfono")
                self._limpiar_formulario()
        except Exception as e:
            print(f"Error detallado: {str(e)}")
            messagebox.showerror("Error", f"Error buscando paciente: {str(e)}")

    def _cargar_datos_paciente(self, paciente):
        print(f"Cargando datos para paciente: {paciente.identificador}")
        print(f"Estado actual de self.personal_vars: {self.personal_vars.keys()}")  # Depuración
        try:
            personal_fields = [
                ("identificador", getattr(paciente, 'identificador', '')),
                ("nombre", getattr(paciente, 'nombre', '')),
                ("fecha_nacimiento", getattr(paciente, 'fecha_nacimiento', '')),
                ("telefono", getattr(paciente, 'telefono', '')),
                ("email", getattr(paciente, 'email', '')),
                ("direccion", getattr(paciente, 'direccion', ''))
            ]
            print(f"Personal fields antes de set: {personal_fields}")
            for field_name, value in personal_fields:
                print(f"Seteando {field_name} con valor: {value}")
                if field_name in self.personal_vars:
                    self.personal_vars[field_name].set(value or "")
                else:
                    raise Exception(f"Clave {field_name} no está definida en self.personal_vars, claves actuales: {self.personal_vars.keys()}")

            historial_fields = [
                ("historial", getattr(paciente, 'historial', '')),
                ("alergias", getattr(paciente, 'alergias', '')),
                ("tratamientos_previos", getattr(paciente, 'tratamientos_previos', '')),
                ("notas", getattr(paciente, 'notas', ''))
            ]
            print(f"Historial fields antes de set: {historial_fields}")
            for field_name, value in historial_fields:
                print(f"Seteando {field_name} con valor: {value}")
                if field_name in self.historial_widgets:
                    text_widget = self.historial_widgets[field_name]
                    text_widget.config(state="normal")
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", value or "")
                    text_widget.config(state="disabled")
                else:
                    raise Exception(f"Clave {field_name} no está definida en self.historial_widgets")
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            raise

    def _cargar_citas(self):
        if self.paciente_id:
            citas = self.controller.db.obtener_citas(self.paciente_id)
            for item in self.tree_citas.get_children():
                self.tree_citas.delete(item)
            for cita in citas:
                # Convertir fecha de YYYY-MM-DD a DD/MM/YY
                fecha_europea = datetime.strptime(cita.fecha, "%Y-%m-%d").strftime("%d/%m/%y")
                self.tree_citas.insert("", tk.END, values=(
                    cita.id_cita, fecha_europea, cita.hora, cita.odontologo, cita.estado
                ))

    def _cargar_visitas(self):
        if self.paciente_id:
            visitas = self.controller.db.obtener_visitas(self.paciente_id)
            for item in self.tree_visitas.get_children():
                self.tree_visitas.delete(item)
            for visita in visitas:
                # Convertir fecha de YYYY-MM-DD a DD/MM/YY
                fecha_europea = datetime.strptime(visita.fecha, "%Y-%m-%d").strftime("%d/%m/%y")
                self.tree_visitas.insert("", tk.END, values=(
                    visita.id_visita, fecha_europea, visita.motivo, visita.diagnostico, visita.odontologo, visita.estado
                ))

    def _cargar_pagos(self):
        if self.paciente_id:
            pagos = self.controller.db.obtener_pagos(self.paciente_id)
            for item in self.tree_pagos.get_children():
                self.tree_pagos.delete(item)
            for pago in pagos:
                # Convertir fecha de YYYY-MM-DD a DD/MM/YY
                fecha_europea = datetime.strptime(pago.fecha_pago, "%Y-%m-%d").strftime("%d/%m/%y")
                self.tree_pagos.insert("", tk.END, values=(
                    pago.id_pago, fecha_europea, f"€{pago.monto_total:.2f}", f"€{pago.monto_pagado:.2f}", pago.metodo, f"€{pago.saldo:.2f}"
                ))

    def _limpiar_formulario(self):
        self.paciente_id = None
        for var in self.personal_vars.values():
            var.set("")
        for widget in self.personal_widgets.values():
            widget.config(state="disabled")
        for text_widget in self.historial_widgets.values():
            text_widget.config(state="normal")
            text_widget.delete("1.0", tk.END)
            text_widget.config(state="disabled")
        for tree in [self.tree_citas, self.tree_visitas, self.tree_pagos]:
            if tree:
                for item in tree.get_children():
                    tree.delete(item)

    def _cerrar_ventana(self):
        if 'pacientes' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['pacientes']
        self.destroy()

    def _abrir_nuevo_paciente(self):
        """Abre la vista para crear un nuevo paciente."""
        print("Abriendo vista para nuevo paciente")
        from views.nuevo_paciente_view import NuevoPacienteView
        nueva_ventana = NuevoPacienteView(self.controller)
        nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: self._actualizar_despues_de_guardar(nueva_ventana))

    def _abrir_editar_paciente(self):
        """Abre la vista para editar el paciente seleccionado."""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        print(f"Abriendo vista para editar paciente: {self.paciente_id}")
        from views.editar_paciente_view import EditarPacienteView
        nueva_ventana = EditarPacienteView(self.controller, self.paciente_id)
        nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: self._actualizar_despues_de_guardar(nueva_ventana))

    def _actualizar_despues_de_guardar(self, ventana):
        """Actualiza la vista principal después de guardar o cerrar la ventana secundaria."""
        ventana.destroy()
        if self.paciente_id:
            paciente = self.controller.db.obtener_paciente(self.paciente_id)
            if paciente:
                self._cargar_datos_paciente(paciente)
                self._cargar_citas()
                self._cargar_visitas()
                self._cargar_pagos()

    def _eliminar_paciente(self):
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de eliminar al paciente {self.paciente_id}?"):
            try:
                self.controller.db.eliminar_paciente(self.paciente_id)
                print(f"Paciente eliminado: {self.paciente_id}")
                self._limpiar_formulario()
                messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
            except Exception as e:
                print(f"Error al eliminar paciente: {str(e)}")
                messagebox.showerror("Error", f"No se pudo eliminar el paciente: {str(e)}")


    def _cargar_pacientes(self):
        """Actualiza la vista principal cargando los datos del paciente seleccionado o limpiando si no hay paciente."""
        print("Actualizando lista de pacientes en PacientesView")
        if self.paciente_id:
            paciente = self.controller.db.obtener_paciente(self.paciente_id)
            if paciente:
                self._cargar_datos_paciente(paciente)
                self._cargar_citas()
                self._cargar_visitas()
                self._cargar_pagos()
            else:
                self._limpiar_formulario()
        else:
            self._limpiar_formulario()
        self.update()  # Refresca la interfaz    
        
    def _abrir_citas_view(self):
        """Abre la vista para gestionar citas del paciente seleccionado."""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        print(f"Abriendo vista para gestionar citas del paciente: {self.paciente_id}")
        from views.citas_view import CitasView
        nueva_ventana = CitasView(self.controller, self.paciente_id)
        nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: self._actualizar_despues_de_guardar(nueva_ventana))

    def _abrir_visitas_view(self):
        """Abre la vista para gestionar visitas del paciente seleccionado."""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        print(f"Abriendo vista para gestionar visitas del paciente: {self.paciente_id}")
        from views.visitas_view import VisitasView
        nueva_ventana = VisitasView(self.controller, self.paciente_id)
        nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: self._actualizar_despues_de_guardar(nueva_ventana))

    def _abrir_pagos_view(self):
        """Abre la vista para gestionar pagos del paciente seleccionado."""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return
        print(f"Abriendo vista para gestionar pagos del paciente: {self.paciente_id}")
        from views.pagos_view import PagosView
        nueva_ventana = PagosView(self.controller, self.paciente_id)
        nueva_ventana.protocol("WM_DELETE_WINDOW", lambda: self._actualizar_despues_de_guardar(nueva_ventana))

    def _on_cita_select(self, event):
        """Almacena la cita seleccionada en el Treeview (para depuración o futuras expansiones)."""
        selected_item = self.tree_citas.selection()
        if selected_item:
            values = self.tree_citas.item(selected_item[0])['values']
            print(f"Cita seleccionada: ID {values[0]}, Fecha {values[1]}")

    def _on_visita_select(self, event):
        """Almacena la visita seleccionada en el Treeview (para depuración o futuras expansiones)."""
        selected_item = self.tree_visitas.selection()
        if selected_item:
            values = self.tree_visitas.item(selected_item[0])['values']
            print(f"Visita seleccionada: ID {values[0]}, Fecha {values[1]}")

    def _on_pago_select(self, event):
        """Almacena el pago seleccionado en el Treeview (para depuración o futuras expansiones)."""
        selected_item = self.tree_pagos.selection()
        if selected_item:
            values = self.tree_pagos.item(selected_item[0])['values']
            print(f"Pago seleccionado: ID {values[0]}, Fecha {values[1]}")
    def _actualizar_sugerencias(self, event=None):
        """Actualiza las sugerencias del Combobox según el texto ingresado."""
        texto_busqueda = self.search_combo.get().strip()
        if not texto_busqueda:
            self.search_combo['values'] = []
            self.pacientes_sugeridos = []  # Limpia la lista de pacientes sugeridos
            return

        try:
            # Obtener pacientes que coincidan con el texto (por identificador o nombre)
            self.pacientes_sugeridos = self.controller.db.buscar_pacientes(texto_busqueda)
            sugerencias = [f"{p.identificador} - {p.nombre}" for p in self.pacientes_sugeridos]
            self.search_combo['values'] = sugerencias[:10]  # Limita a 10 sugerencias
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar sugerencias: {str(e)}")
    def _on_sugerencia_seleccionada(self, event):
        """Al seleccionar una sugerencia, inserta solo el identificador y busca al paciente."""
        seleccion = self.search_combo.get()
        if seleccion and self.pacientes_sugeridos:
            # Extraer el identificador de la cadena formateada (por ejemplo, "12345678X - Juan Pérez")
            identificador = seleccion.split(" - ")[0]  # Toma solo "12345678X"
            self.search_combo.set(identificador)  # Inserta solo el DNI/NIE en el campo
            self._buscar_paciente()  # Busca automáticamente el paciente
    def _editar_cita(self, event):
        """Abre un diálogo para editar la cita seleccionada en el Treeview."""
        selected_item = self.tree_citas.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona una cita primero")
            return

        values = self.tree_citas.item(selected_item[0])['values']
        if not values or len(values) < 5:
            messagebox.showerror("Error", "Datos de cita inválidos")
            return

        id_cita, fecha, hora, odontologo, estado = values

        # Convertir fecha de YYYY-MM-DD a DD/MM/YY para la entrada
        fecha_europea = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%y")

        # Crear una ventana de edición
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Editar Cita ID: {id_cita}")
        edit_window.geometry("400x300")
        edit_window.transient(self)
        edit_window.grab_set()

        # Campos de edición
        ttk.Label(edit_window, text="Fecha (DD/MM/YY):").pack(pady=5)
        fecha_var = tk.StringVar(value=fecha_europea)
        fecha_entry = ttk.Entry(edit_window, textvariable=fecha_var)
        fecha_entry.pack(pady=5)

        ttk.Label(edit_window, text="Hora (HH:MM):").pack(pady=5)
        hora_var = tk.StringVar(value=hora)
        hora_entry = ttk.Entry(edit_window, textvariable=hora_var)
        hora_entry.pack(pady=5)

        ttk.Label(edit_window, text="Odontólogo:").pack(pady=5)
        odontologo_var = tk.StringVar(value=odontologo)
        odontologo_entry = ttk.Entry(edit_window, textvariable=odontologo_var)
        odontologo_entry.pack(pady=5)

        ttk.Label(edit_window, text="Estado:").pack(pady=5)
        estado_var = tk.StringVar(value=estado)
        estado_combo = ttk.Combobox(edit_window, textvariable=estado_var, values=["Pendiente", "Confirmada", "Cancelada", "Completada"])
        estado_combo.pack(pady=5)

        def guardar_cambios_cita(fecha_var_param, hora_var_param, odontologo_var_param, estado_var_param):
            try:
                nueva_fecha_europea = fecha_var_param.get().strip()
                # Validar y convertir fecha de DD/MM/YY a YYYY-MM-DD
                try:
                    nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
                except ValueError as ve:
                    raise ValueError("Formato de fecha inválido. Usa DD/MM/YY (por ejemplo, 25/02/25)")

                nueva_hora = hora_var_param.get().strip()
                nuevo_odontologo = odontologo_var_param.get().strip()
                nuevo_estado = estado_var_param.get().strip()

                if not all([nueva_fecha, nueva_hora, nuevo_odontologo, nuevo_estado]):
                    raise ValueError("Todos los campos son obligatorios")

                # Verificar disponibilidad del odontólogo (puedes añadir esta validación aquí si ya la tienes en DatabaseService)
                if not self.controller.db.verificar_disponibilidad_cita(nueva_fecha, nueva_hora, nuevo_odontologo):
                    raise ValueError("El odontólogo no está disponible en esa fecha y hora")

                from models.cita import Cita
                cita = Cita(id_cita, self.paciente_id, nueva_fecha, nueva_hora, nuevo_odontologo, nuevo_estado)
                self.controller.db.actualizar_cita(cita)

                self._cargar_citas()
                messagebox.showinfo("Éxito", "Cita actualizada correctamente")
                edit_window.destroy()
            except ValueError as ve:
                messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar la cita: {str(e)}")

        ttk.Button(edit_window, text="Guardar", command=lambda: guardar_cambios_cita(fecha_var, hora_var, odontologo_var, estado_var)).pack(pady=10)
        ttk.Button(edit_window, text="Cancelar", command=edit_window.destroy).pack(pady=5)
    
    def _editar_visita(self, event):
        """Abre un diálogo para editar la visita seleccionada en el Treeview."""
        selected_item = self.tree_visitas.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona una visita primero")
            return

        values = self.tree_visitas.item(selected_item[0])['values']
        if not values or len(values) < 6:
            messagebox.showerror("Error", "Datos de visita inválidos")
            return

        id_visita, fecha, motivo, diagnostico, odontologo, estado = values

        # Convertir fecha de YYYY-MM-DD a DD/MM/YY para la entrada
        fecha_europea = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%y")

        # Crear una ventana de edición
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Editar Visita ID: {id_visita}")
        edit_window.geometry("400x400")
        edit_window.transient(self)
        edit_window.grab_set()

        # Campos de edición
        ttk.Label(edit_window, text="Fecha (DD/MM/YY):").pack(pady=5)
        fecha_var = tk.StringVar(value=fecha_europea)
        fecha_entry = ttk.Entry(edit_window, textvariable=fecha_var)
        fecha_entry.pack(pady=5)

        ttk.Label(edit_window, text="Motivo:").pack(pady=5)
        motivo_var = tk.StringVar(value=motivo)
        motivo_entry = ttk.Entry(edit_window, textvariable=motivo_var)
        motivo_entry.pack(pady=5)

        ttk.Label(edit_window, text="Diagnóstico:").pack(pady=5)
        diagnostico_var = tk.StringVar(value=diagnostico)
        diagnostico_entry = ttk.Entry(edit_window, textvariable=diagnostico_var)
        diagnostico_entry.pack(pady=5)

        ttk.Label(edit_window, text="Odontólogo:").pack(pady=5)
        odontologo_var = tk.StringVar(value=odontologo)
        odontologo_entry = ttk.Entry(edit_window, textvariable=odontologo_var)
        odontologo_entry.pack(pady=5)

        ttk.Label(edit_window, text="Estado:").pack(pady=5)
        estado_var = tk.StringVar(value=estado)
        estado_combo = ttk.Combobox(edit_window, textvariable=estado_var, values=["Pendiente", "Completada", "Cancelada"])
        estado_combo.pack(pady=5)

        def guardar_cambios_visita(fecha_var_param, motivo_var_param, diagnostico_var_param, odontologo_var_param, estado_var_param):
            try:
                nueva_fecha_europea = fecha_var_param.get().strip()
                # Validar y convertir fecha de DD/MM/YY a YYYY-MM-DD
                try:
                    nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
                except ValueError as ve:
                    raise ValueError("Formato de fecha inválido. Usa DD/MM/YY (por ejemplo, 25/02/25)")

                nuevo_motivo = motivo_var_param.get().strip()
                nuevo_diagnostico = diagnostico_var_param.get().strip()
                nuevo_odontologo = odontologo_var_param.get().strip()
                nuevo_estado = estado_var_param.get().strip()

                if not all([nueva_fecha, nuevo_motivo, nuevo_odontologo, nuevo_estado]):
                    raise ValueError("Todos los campos son obligatorios")

                from models.visita import Visita
                visita = Visita(id_visita, self.paciente_id, nueva_fecha, nuevo_motivo, nuevo_diagnostico, nuevo_odontologo, nuevo_estado)
                self.controller.db.actualizar_visita(visita)

                self._cargar_visitas()
                messagebox.showinfo("Éxito", "Visita actualizada correctamente")
                edit_window.destroy()
            except ValueError as ve:
                messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar la visita: {str(e)}")

        ttk.Button(edit_window, text="Guardar", command=lambda: guardar_cambios_visita(fecha_var, motivo_var, diagnostico_var, odontologo_var, estado_var)).pack(pady=10)
        ttk.Button(edit_window, text="Cancelar", command=edit_window.destroy).pack(pady=5)
    def _crear_lista_pagos(self, frame):
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Gestionar Pagos", command=lambda: self._abrir_pagos_view()).pack(side=tk.LEFT, padx=5)

        self.tree_pagos = ttk.Treeview(frame, columns=("ID", "Fecha", "Monto Total", "Pagado", "Método", "Saldo"), show="headings", height=5)
        for col in self.tree_pagos["columns"]:
            self.tree_pagos.heading(col, text=col)
            self.tree_pagos.column(col, width=120, anchor=tk.W, stretch=tk.YES)
        self.tree_pagos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Vincular eventos: selección y doble clic para edición
        self.tree_pagos.bind("<<TreeviewSelect>>", self._on_pago_select)
        self.tree_pagos.bind("<Double-1>", self._editar_pago)  # Añadir edición con doble clic  
    def _editar_pago(self, event):
        """Abre un diálogo para editar el pago seleccionado en el Treeview."""
        selected_item = self.tree_pagos.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Selecciona un pago primero")
            return

        values = self.tree_pagos.item(selected_item[0])['values']
        if not values or len(values) < 6:
            messagebox.showerror("Error", "Datos de pago inválidos")
            return

        id_pago, fecha, monto_total, monto_pagado, metodo, saldo = values

        # Convertir fecha de YYYY-MM-DD a DD/MM/YY para la entrada
        fecha_europea = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%y")

        # Crear una ventana de edición
        edit_window = tk.Toplevel(self)
        edit_window.title(f"Editar Pago ID: {id_pago}")
        edit_window.geometry("400x300")
        edit_window.transient(self)
        edit_window.grab_set()

        # Campos de edición
        ttk.Label(edit_window, text="Fecha (DD/MM/YY):").pack(pady=5)
        fecha_var = tk.StringVar(value=fecha_europea)
        fecha_entry = ttk.Entry(edit_window, textvariable=fecha_var)
        fecha_entry.pack(pady=5)

        ttk.Label(edit_window, text="Monto Total (€):").pack(pady=5)
        monto_total_var = tk.StringVar(value=monto_total.replace("€", "").strip())
        monto_total_entry = ttk.Entry(edit_window, textvariable=monto_total_var)
        monto_total_entry.pack(pady=5)

        ttk.Label(edit_window, text="Monto Pagado (€):").pack(pady=5)
        monto_pagado_var = tk.StringVar(value=monto_pagado.replace("€", "").strip())
        monto_pagado_entry = ttk.Entry(edit_window, textvariable=monto_pagado_var)
        monto_pagado_entry.pack(pady=5)

        ttk.Label(edit_window, text="Método:").pack(pady=5)
        metodo_var = tk.StringVar(value=metodo)
        metodo_combo = ttk.Combobox(edit_window, textvariable=metodo_var, values=["Efectivo", "Tarjeta", "Transferencia"])
        metodo_combo.pack(pady=5)

        def guardar_cambios_pago(fecha_var_param, monto_total_var_param, monto_pagado_var_param, metodo_var_param):
            try:
                nueva_fecha_europea = fecha_var_param.get().strip()
                # Validar y convertir fecha de DD/MM/YY a YYYY-MM-DD
                try:
                    nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
                except ValueError as ve:
                    raise ValueError("Formato de fecha inválido. Usa DD/MM/YY (por ejemplo, 25/02/25)")

                nuevo_monto_total = float(monto_total_var_param.get().strip())
                nuevo_monto_pagado = float(monto_pagado_var_param.get().strip())
                nuevo_metodo = metodo_var_param.get().strip()

                if not all([nueva_fecha, nuevo_monto_total, nuevo_monto_pagado, nuevo_metodo]):
                    raise ValueError("Todos los campos son obligatorios")

                # Calcular nuevo saldo
                nuevo_saldo = nuevo_monto_total - nuevo_monto_pagado

                from models.pago import Pago
                pago = Pago(id_pago, None, self.paciente_id, nuevo_monto_total, nuevo_monto_pagado, nueva_fecha, nuevo_metodo, nuevo_saldo)
                self.controller.db.actualizar_pago(pago)

                self._cargar_pagos()
                messagebox.showinfo("Éxito", "Pago actualizado correctamente")
                edit_window.destroy()
            except ValueError as ve:
                messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar el pago: {str(e)}")

        ttk.Button(edit_window, text="Guardar", command=lambda: guardar_cambios_pago(fecha_var, monto_total_var, monto_pagado_var, metodo_var)).pack(pady=10)
        ttk.Button(edit_window, text="Cancelar", command=edit_window.destroy).pack(pady=5)                                      
                      