# ARCHIVO views/paciente_view.py
import sys
from tkinter import font
from PIL import Image, ImageDraw, ImageFont  # Añadido PIL.Image explícitamente
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from services.database_service import DatabaseService
from models.paciente import Paciente
from models.cita import Cita
from models.visita import Visita
from datetime import datetime
from views.styles import configurar_estilos
from models.odontograma import Odontograma
import os
from reportlab.pdfgen import canvas as pdfcanvas
import io
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from models.pago import Pago




class PacientesView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Gestión de Pacientes Clínica P&D")
        self.resizable(True, True)
        self.paciente_id = None
        self.personal_vars = {}
        self.personal_widgets = {}
        self.historial_widgets = {}
        self._crear_widgets()
        self._inicializar_posicion()
        configurar_estilos(self)
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)
        self.notebook.bind("<<NotebookTabChanged>>", self._ajustar_tamanio_ventana)

    def _inicializar_posicion(self):
        self.update_idletasks()
        ancho = 800
        alto = 500
        self.geometry(f"{ancho}x{alto}+100+100")

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
        style = ttk.Style()
        style.configure("Label", font=("Arial", 12))
        ttk.Label(search_frame, text="Buscar Paciente:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.search_combo = ttk.Combobox(search_frame, width=40)
        
        self.search_combo.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        self.search_combo.bind('<KeyRelease>', self._actualizar_sugerencias)
        self.search_combo.bind('<Return>', lambda event: self._buscar_paciente())
        self.search_combo.bind('<<ComboboxSelected>>', self._on_sugerencia_seleccionada)

        ttk.Button(search_frame, text="Buscar", command=self._buscar_paciente).grid(row=0, column=2, padx=5, pady=5)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Agregar Paciente", command=self._abrir_nuevo_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar", command=self._abrir_editar_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar", command=self._eliminar_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar Información", command=self._exportar_informacion_a_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exportar Odontograma", command=self._exportar_odontograma_a_pdf).pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=("Arial", 12))
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
        
        odontograma_frame = ttk.Frame(self.notebook)
        self.notebook.add(odontograma_frame, text="Odontograma")
        self._crear_odontograma_pro(odontograma_frame)

    def _ajustar_tamanio_ventana(self, event):
        tab_id = self.notebook.tab(self.notebook.select(), "text")
        ancho_base = 800
        alto_minimo = 550

        if tab_id == "Información Personal":
            alto = 400
        elif tab_id == "Historial Médico":
            alto = 500
        elif tab_id == "Citas":
            alto = 550
        elif tab_id == "Visitas":
            alto = 550
        elif tab_id == "Pagos y Deudas":
            alto = 600
        elif tab_id == "Odontograma":
            alto = 700    
        else:
            alto = 500

        alto = max(alto, alto_minimo)
        current_x = self.winfo_x()
        current_y = self.winfo_y()
        self.geometry(f"{ancho_base}x{alto}+{current_x}+{current_y}")
        self.update_idletasks()

    def _crear_formulario_personal(self, frame):
        fields = [
            ("DNI/NIF/NIE", 25),
            ("Nombre", 30),
            ("Fecha Nacimiento", 15),
            ("Teléfono", 15),
            ("Email", 30),
            ("Dirección", 40)
        ]
        self.personal_widgets = {}
        
        # Definir la fuente personalizada (puedes cambiar "Arial" y 12 por lo que desees)
        fuente_personalizada = font.Font(family="Arial", size=12)  # Ejemplo: Arial, tamaño 12
        
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
            # Aplicar la fuente personalizada al Entry
            entry = ttk.Entry(frame, textvariable=var, width=width, font=fuente_personalizada, state="disabled")
            
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.personal_widgets[key] = entry
            
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
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Gestionar Citas", command=lambda: self._abrir_citas_view()).pack(side=tk.LEFT, padx=5)

        self.tree_citas = ttk.Treeview(frame, columns=("ID", "Fecha", "Hora", "Odontólogo", "Estado"), show="headings", height=5)
        for col in self.tree_citas["columns"]:
            self.tree_citas.heading(col, text=col)
            self.tree_citas.column(col, width=120, anchor=tk.W, stretch=tk.YES)
        self.tree_citas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_citas.bind("<<TreeviewSelect>>", self._on_cita_select)
        self.tree_citas.bind("<Double-1>", self._editar_cita)

    def _crear_lista_visitas(self, frame):
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Gestionar Visitas", command=lambda: self._abrir_visitas_view()).pack(side=tk.LEFT, padx=5)

        self.tree_visitas = ttk.Treeview(frame, columns=("ID", "Fecha", "Motivo", "Diagnóstico", "Odontólogo", "Estado"), show="headings", height=5)
        for col in self.tree_visitas["columns"]:
            self.tree_visitas.heading(col, text=col)
            self.tree_visitas.column(col, width=120, anchor=tk.W, stretch=tk.YES)
        self.tree_visitas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_visitas.bind("<<TreeviewSelect>>", self._on_visita_select)
        self.tree_visitas.bind("<Double-1>", self._editar_visita)

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

        # La fecha ya está en DD/MM/YY desde el Treeview, no necesita conversión
        fecha_europea = fecha
        
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

        def guardar_cambios_visita():
            try:
                nueva_fecha_europea = fecha_var.get().strip()
                # Convertir de DD/MM/YY a YYYY-MM-DD
                nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
                nuevo_motivo = motivo_var.get().strip()
                nuevo_diagnostico = diagnostico_var.get().strip()
                nuevo_odontologo = odontologo_var.get().strip()
                nuevo_estado = estado_var.get().strip()

                if not all([nueva_fecha, nuevo_motivo, nuevo_odontologo, nuevo_estado]):
                    raise ValueError("Todos los campos son obligatorios")

                from models.visita import Visita
                visita = Visita(id_visita, self.paciente_id, nueva_fecha, nuevo_motivo, nuevo_diagnostico, "", nuevo_odontologo, nuevo_estado)  # Tratamiento vacío por ahora
                self.controller.db.actualizar_visita(visita)
                self._cargar_visitas()
                messagebox.showinfo("Éxito", "Visita actualizada correctamente")
                edit_window.destroy()
            except ValueError as ve:
                messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo actualizar la visita: {str(e)}")

        ttk.Button(edit_window, text="Guardar", command=guardar_cambios_visita).pack(pady=10)
        ttk.Button(edit_window, text="Cancelar", command=edit_window.destroy).pack(pady=5)

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

        # La fecha ya está en DD/MM/YY desde el Treeview, no necesita conversión
        fecha_europea = fecha
        
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

        def guardar_cambios_cita():
            try:
                nueva_fecha_europea = fecha_var.get().strip()
                # Convertir de DD/MM/YY a YYYY-MM-DD
                nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
                nueva_hora = hora_var.get().strip()
                nuevo_odontologo = odontologo_var.get().strip()
                nuevo_estado = estado_var.get().strip()

                if not all([nueva_fecha, nueva_hora, nuevo_odontologo, nuevo_estado]):
                    raise ValueError("Todos los campos son obligatorios")

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

        ttk.Button(edit_window, text="Guardar", command=guardar_cambios_cita).pack(pady=10)
        ttk.Button(edit_window, text="Cancelar", command=edit_window.destroy).pack(pady=5)

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

        # La fecha ya está en DD/MM/YY desde el Treeview, no necesita conversión
        fecha_europea = fecha
        
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

        def guardar_cambios_pago():
            try:
                nueva_fecha_europea = fecha_var.get().strip()
                nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
                nuevo_monto_total = float(monto_total_var.get().strip())
                nuevo_monto_pagado = float(monto_pagado_var.get().strip())
                nuevo_metodo = metodo_var.get().strip()

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

        ttk.Button(edit_window, text="Guardar", command=guardar_cambios_pago).pack(pady=10)
        ttk.Button(edit_window, text="Cancelar", command=edit_window.destroy).pack(pady=5)

    def _crear_lista_pagos(self, frame):
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Gestionar Pagos", command=lambda: self._abrir_pagos_view()).pack(side=tk.LEFT, padx=5)

        self.tree_pagos = ttk.Treeview(frame, columns=("ID", "Fecha", "Monto Total", "Pagado", "Método", "Saldo"), show="headings", height=5)
        for col in self.tree_pagos["columns"]:
            self.tree_pagos.heading(col, text=col)
            self.tree_pagos.column(col, width=100, anchor=tk.W, stretch=tk.YES)
        self.tree_pagos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree_pagos.bind("<<TreeviewSelect>>", self._on_pago_select)
        self.tree_pagos.bind("<Double-1>", self._editar_pago)

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
                    self._load_odontogram()  # Corregido de _cargar_odontograma a _load_odontogram
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
                ("nombre", getattr(paciente, 'nombre', '')),  # Este será modificado más abajo
                ("fecha_nacimiento", getattr(paciente, 'fecha_nacimiento', '')),
                ("telefono", getattr(paciente, 'telefono', '')),
                ("email", getattr(paciente, 'email', '')),
                ("direccion", getattr(paciente, 'direccion', ''))
            ]
            print(f"Personal fields antes de set: {personal_fields}")
            for field_name, value in personal_fields:
                print(f"Seteando {field_name} con valor: {value}")
                if field_name in self.personal_vars:
                    # Aplicar .title() solo al campo "nombre"
                    if field_name == "nombre" and value:  # Verificar que value no esté vacío
                        value = value.title()  # Capitaliza "juan perez" → "Juan Perez"
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
                self._load_odontogram()  # Corrección: Cambiado de _cargar_odontograma a _load_odontogram

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
            self.pacientes_sugeridos = []
            return

        try:
            # Obtener pacientes que coincidan con el texto
            self.pacientes_sugeridos = self.controller.db.buscar_pacientes(texto_busqueda)
            # Aplicar .title() al nombre en las sugerencias
            sugerencias = [f"{p.identificador} - {p.nombre.title()}" for p in self.pacientes_sugeridos]
            self.search_combo['values'] = sugerencias[:10]  # Limita a 10 sugerencias
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar sugerencias: {str(e)}")

    def _on_sugerencia_seleccionada(self, event):
        """Al seleccionar una sugerencia, inserta solo el identificador y busca al paciente."""
        seleccion = self.search_combo.get()
        if seleccion and self.pacientes_sugeridos:
            identificador = seleccion.split(" - ")[0]
            self.search_combo.set(identificador)
            self._buscar_paciente()

    def _crear_odontograma_pro(self, frame):
        self.canvas = tk.Canvas(frame, width=800, height=500, bg="white")
        self.canvas.pack(pady=10)

        self.selected_tool = tk.StringVar(value="Caries")
        self.dientes = {}

        self.icons = self._load_icons()
        self._create_toolbar(frame)
        self._create_legend(frame)
        self._draw_odontogram()

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Button-3>", self._show_history)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Guardar", command=self._save_odontogram).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Exportar PDF", command=self._exportar_paciente_a_pdf).pack(side=tk.LEFT, padx=5)  # Ajustado para usar el nuevo método

        # Cargar odontograma si existe y renderizar
        if self.paciente_id:
            self._load_odontogram()
        self.canvas.update()  # Asegurar que el Canvas se renderice

    def _load_icons(self):
        icons = {}
        image_folder = os.path.join(Path(__file__).resolve().parent.parent, "imagenes")
        for tool in ["Caries", "Extracción", "Restauración", "Implante", "Endodoncia", "Normal"]:
            file_path = os.path.join(image_folder, f"{tool.lower()}.png")
            try:
                img = Image.open(file_path).resize((16, 16), Image.LANCZOS)
                icons[tool] = Image.PhotoImage(img)
            except (FileNotFoundError, Exception):
                print(f"Advertencia: No se encontró {file_path}. Usando sin ícono.")
                icons[tool] = None
        return icons

    def _create_toolbar(self, frame):
        toolbar = ttk.Frame(frame)
        toolbar.pack(pady=5)
        tools = ["Caries", "Extracción", "Restauración", "Implante", "Endodoncia", "Normal"]
        for tool in tools:
            frame_tool = ttk.Frame(toolbar)
            frame_tool.pack(side=tk.LEFT, padx=5)
            btn = ttk.Radiobutton(frame_tool, value=tool, variable=self.selected_tool)
            btn.pack(side=tk.LEFT)
            if self.icons[tool]:
                tk.Label(frame_tool, image=self.icons[tool]).pack(side=tk.LEFT)
            tk.Label(frame_tool, text=tool).pack(side=tk.LEFT)

    def _create_legend(self, frame):
        legend_frame = ttk.LabelFrame(frame, text="Leyenda")
        legend_frame.pack(pady=5, padx=10, fill="x")
        colors = {"Caries": "yellow", "Extracción": "red", "Restauración": "blue", 
                "Implante": "silver", "Endodoncia": "purple", "Normal": "white"}
        for state, color in colors.items():
            frame_legend = ttk.Frame(legend_frame)
            frame_legend.pack(side=tk.LEFT, padx=5)
            tk.Label(frame_legend, bg=color, width=2, height=1, borderwidth=1, relief="solid").pack(side=tk.LEFT)
            tk.Label(frame_legend, text=state).pack(side=tk.LEFT)

    def _draw_tooth(self, x, y, tooth_id):
        faces = {
            "oclusal": self.canvas.create_rectangle(x+5, y+5, x+25, y+15, fill="white", outline="black"),
            "mesial": self.canvas.create_rectangle(x, y+15, x+10, y+35, fill="white", outline="black"),
            "distal": self.canvas.create_rectangle(x+20, y+15, x+30, y+35, fill="white", outline="black"),
            "vestibular": self.canvas.create_rectangle(x+10, y, x+20, y+10, fill="white", outline="black"),
            "lingual": self.canvas.create_rectangle(x+10, y+30, x+20, y+40, fill="white", outline="black")
        }
        self.canvas.create_text(x+15, y+50, text=tooth_id, font=("Arial", 10))
        self.dientes[tooth_id] = {"id": tooth_id, "faces": faces, "state": {}, "history": [], "locked": False}
        return faces

    def _draw_odontogram(self):
        self.canvas.create_line(400, 0, 400, 500, dash=(4, 2))
        self.canvas.create_line(0, 250, 800, 250, dash=(4, 2))

        for i in range(8):
            self._draw_tooth(400 - (i+1) * 40, 50, f"1{i+1}")
            self._draw_tooth(400 + i * 40, 50, f"2{i+1}")
            self._draw_tooth(400 + i * 40, 300, f"3{i+1}")
            self._draw_tooth(400 - (i+1) * 40, 300, f"4{i+1}")

    def _on_click(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        for tooth_id, tooth in self.dientes.items():
            for face, face_id in tooth["faces"].items():
                if face_id == item:
                    tool = self.selected_tool.get()
                    colors = {"Caries": "yellow", "Extracción": "red", "Restauración": "blue", 
                            "Implante": "silver", "Endodoncia": "purple", "Normal": "white"}

                    if tooth["locked"] and tool not in ["Extracción", "Implante", "Endodoncia"]:
                        messagebox.showwarning("Bloqueado", f"El diente {tooth_id} está extraído, implantado o con endodoncia.")
                        return

                    if tool in ["Extracción", "Implante", "Endodoncia"]:
                        for f_id in tooth["faces"].values():
                            self.canvas.itemconfig(f_id, fill=colors[tool])
                        tooth["state"] = {face: tool for face in tooth["faces"]}
                        tooth["locked"] = True
                        tooth["history"].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Diente completo marcado como {tool}")
                        messagebox.showinfo("Acción", f"Diente {tooth_id} marcado como {tool}")
                    else:
                        self.canvas.itemconfig(face_id, fill=colors[tool])
                        tooth["state"][face] = tool
                        tooth["history"].append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {face} marcada como {tool}")
                        messagebox.showinfo("Acción", f"Cara {face} del diente {tooth_id} marcada como {tool}")
                    return

    def _show_history(self, event):
        item = self.canvas.find_closest(event.x, event.y)[0]
        for tooth_id, tooth in self.dientes.items():
            for face_id in tooth["faces"].values():
                if face_id == item:
                    history = "\n".join(tooth["history"]) if tooth["history"] else "Sin historial."
                    messagebox.showinfo(f"Historial de {tooth_id}", history)
                    return

    def _save_odontogram(self):
        if self.paciente_id:
            odontograma_data = {k: {"id": v["id"], "state": v["state"], "history": v["history"], "locked": v["locked"]} 
                            for k, v in self.dientes.items()}
            try:
                self.controller.db.guardar_odontograma(Odontograma(self.paciente_id, odontograma_data))
                messagebox.showinfo("Guardado", "Odontograma guardado correctamente")
                print(f"Odontograma guardado para paciente_id={self.paciente_id}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el odontograma: {str(e)}")
                print(f"Error al guardar odontograma: {str(e)}")

    def _load_odontogram(self):
        if self.paciente_id:
            try:
                odontograma = self.controller.db.obtener_odontograma(self.paciente_id)
                if odontograma.dientes:
                    for tooth_id, info in odontograma.dientes.items():
                        if tooth_id in self.dientes:
                            for face, state in info["state"].items():
                                color = {"Caries": "yellow", "Extracción": "red", "Restauración": "blue", 
                                        "Implante": "silver", "Endodoncia": "purple", "Normal": "white"}[state]
                                self.canvas.itemconfig(self.dientes[tooth_id]["faces"][face], fill=color)
                            self.dientes[tooth_id]["state"] = info["state"]
                            self.dientes[tooth_id]["history"] = info["history"]
                            self.dientes[tooth_id]["locked"] = info.get("locked", False)
                messagebox.showinfo("Cargado", "Odontograma cargado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el odontograma: {str(e)}")
                print(f"Error al cargar odontograma: {str(e)}")
    def _exportar_informacion_a_pdf(self):
        """Exporta la información general del paciente (personal, historial, citas, visitas, pagos) y el informe del estado de los dientes a un archivo PDF."""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return

        # Obtener datos del paciente
        paciente = self.controller.db.obtener_paciente(self.paciente_id)
        if not paciente:
            messagebox.showerror("Error", "No se pudo encontrar el paciente")
            return

        # Obtener citas, visitas, pagos y odontograma
        citas = self.controller.db.obtener_citas(self.paciente_id)
        visitas = self.controller.db.obtener_visitas(self.paciente_id)
        pagos = self.controller.db.obtener_pagos(self.paciente_id)
        odontograma = self.controller.db.obtener_odontograma(self.paciente_id)

        # Determinar estado predominante de cada diente
        tooth_states = {}
        if odontograma and odontograma.dientes:
            for tooth_id, info in odontograma.dientes.items():
                if info.get("locked", False):
                    state = info["state"].get("oclusal", "Normal")
                else:
                    states = [info["state"].get(face, "Normal") for face in ["oclusal", "mesial", "distal", "vestibular", "lingual"]]
                    state = max(set(states), key=states.count) if states else "Normal"
                tooth_states[tooth_id] = state

        # Ordenar dientes
        sorted_teeth = sorted(tooth_states.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))

        # Abrir diálogo para guardar el archivo
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], 
                                                initialfile=f"Informacion_Paciente_{self.paciente_id}.pdf")
        if not file_path:
            return

        # Crear el documento PDF
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        style_normal = styles["Normal"]
        style_title = ParagraphStyle(name="Title", parent=styles["Heading1"], fontSize=16, alignment=1)
        style_subtitle = ParagraphStyle(name="Subtitle", parent=styles["Heading2"], fontSize=12)

        # Elementos del PDF
        elements = []

        # Título con nombre y DNI
        title_text = f"Información del Paciente - {getattr(paciente, 'nombre', 'N/A').title()} - ID: {self.paciente_id}"
        elements.append(Paragraph(title_text, style_title))
        elements.append(Spacer(1, 10))

        # Información Personal
        elements.append(Paragraph("Información Personal", style_subtitle))
        elements.append(Paragraph(f"DNI/NIF/NIE: {getattr(paciente, 'identificador', 'N/A')}", style_normal))
        elements.append(Paragraph(f"Nombre: {getattr(paciente, 'nombre', 'N/A').title()}", style_normal))  # Capitalizar nombre
        elements.append(Paragraph(f"Fecha Nacimiento: {getattr(paciente, 'fecha_nacimiento', 'N/A')}", style_normal))
        elements.append(Paragraph(f"Teléfono: {getattr(paciente, 'telefono', 'N/A')}", style_normal))
        elements.append(Paragraph(f"Email: {getattr(paciente, 'email', 'N/A')}", style_normal))
        elements.append(Paragraph(f"Dirección: {getattr(paciente, 'direccion', 'N/A')}", style_normal))
        elements.append(Spacer(1, 10))

        # Historial Médico
        elements.append(Paragraph("Historial Médico", style_subtitle))
        elements.append(Paragraph(f"Historial: {getattr(paciente, 'historial', 'N/A')}", style_normal))
        elements.append(Paragraph(f"Alergias: {getattr(paciente, 'alergias', 'N/A')}", style_normal))
        elements.append(Paragraph(f"Tratamientos Previos: {getattr(paciente, 'tratamientos_previos', 'N/A')}", style_normal))
        elements.append(Paragraph(f"Notas: {getattr(paciente, 'notas', 'N/A')}", style_normal))
        elements.append(Spacer(1, 10))

        # Citas
        elements.append(Paragraph("Citas", style_subtitle))
        for cita in citas:
            fecha_europea = datetime.strptime(cita.fecha, "%Y-%m-%d").strftime("%d/%m/%y")
            elements.append(Paragraph(f"ID: {cita.id_cita}, Fecha: {fecha_europea}, Hora: {cita.hora}, Odontólogo: {cita.odontologo}, Estado: {cita.estado}", style_normal))
        elements.append(Spacer(1, 10))

        # Visitas
        elements.append(Paragraph("Visitas", style_subtitle))
        for visita in visitas:
            fecha_europea = datetime.strptime(visita.fecha, "%Y-%m-%d").strftime("%d/%m/%y")
            elements.append(Paragraph(f"ID: {visita.id_visita}, Fecha: {fecha_europea}, Motivo: {visita.motivo}, Diagnóstico: {visita.diagnostico}, Odontólogo: {visita.odontologo}, Estado: {visita.estado}", style_normal))
        elements.append(Spacer(1, 10))

        # Pagos y Deudas
        elements.append(Paragraph("Pagos y Deudas", style_subtitle))
        for pago in pagos:
            fecha_europea = datetime.strptime(pago.fecha_pago, "%Y-%m-%d").strftime("%d/%m/%y")
            elements.append(Paragraph(f"ID: {pago.id_pago}, Fecha: {fecha_europea}, Monto Total: €{pago.monto_total:.2f}, Pagado: €{pago.monto_pagado:.2f}, Método: {pago.metodo}, Saldo: €{pago.saldo:.2f}", style_normal))
        elements.append(Spacer(1, 10))

        # Informe del Estado de los Dientes
        elements.append(Paragraph("Informe del Estado de los Dientes", style_subtitle))
        data = [["Diente", "Estado"]]
        for tooth_id in sorted_teeth:
            data.append([tooth_id, tooth_states[tooth_id]])
        table = Table(data, colWidths=[40, 300], rowHeights=12)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(table)

        # Finalizar el documento
        doc.build(elements)
        messagebox.showinfo("Éxito", f"Información del paciente exportada a {file_path}")

    
    def _exportar_odontograma_a_pdf(self):
        """Exporta solo la imagen del odontograma del paciente seleccionado a un archivo PDF en orientación horizontal con nombre y DNI."""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Selecciona un paciente primero")
            return

        # Obtener datos del paciente y odontograma
        paciente = self.controller.db.obtener_paciente(self.paciente_id)
        if not paciente:
            messagebox.showerror("Error", "No se pudo encontrar el paciente")
            return
        odontograma = self.controller.db.obtener_odontograma(self.paciente_id)
        if not odontograma or not odontograma.dientes:
            messagebox.showerror("Error", "No se encontraron datos de odontograma para este paciente")
            return

        # Renderizar el odontograma como imagen con Pillow
        img_width, img_height = 750, 350  # Reducir tamaño para evitar cortes
        img = Image.new('RGB', (img_width, img_height), color='white')
        draw = ImageDraw.Draw(img)
        colors = {"Caries": "yellow", "Extracción": "red", "Restauración": "blue", 
                "Implante": "silver", "Endodoncia": "purple", "Normal": "white"}

        # Dibujar líneas del odontograma
        draw.line([(375, 0), (375, img_height)], fill="black", width=1)  # Ajustar al nuevo tamaño
        draw.line([(0, 175), (img_width, 175)], fill="black", width=1)   # Ajustar al nuevo tamaño

        # Dibujar dientes
        for i in range(8):
            x1, y1 = 375 - (i+1) * 47, 25  # Ajustar escala
            x2, y2 = 375 + i * 47, 25
            x3, y3 = 375 + i * 47, 300
            x4, y4 = 375 - (i+1) * 47, 300
            tooth_ids = [f"1{i+1}", f"2{i+1}", f"3{i+1}", f"4{i+1}"]
            coords = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            for (x, y), tooth_id in zip(coords, tooth_ids):
                faces = {
                    "oclusal": [(x+5, y+5), (x+15, y+15)],
                    "mesial": [(x, y+15), (x+5, y+30)],
                    "distal": [(x+15, y+15), (x+20, y+30)],
                    "vestibular": [(x+5, y), (x+15, y+5)],
                    "lingual": [(x+5, y+30), (x+15, y+35)]
                }
                for face, (start, end) in faces.items():
                    state = odontograma.dientes.get(tooth_id, {}).get("state", {}).get(face, "Normal")
                    draw.rectangle([start, end], fill=colors[state], outline="black")
                draw.text((x+10, y+40), tooth_id, fill="black")

        # Guardar imagen temporal
        img_path = "temp_odontograma.png"
        img.save(img_path, dpi=(150, 150))

        # Abrir diálogo para guardar el archivo
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], 
                                                initialfile=f"Odontograma_Paciente_{self.paciente_id}.pdf")
        if not file_path:
            os.remove(img_path)  # Limpiar archivo temporal si se cancela
            return

        # Crear el documento PDF en orientación horizontal
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        doc.pagesize = (letter[1], letter[0])  # Orientación horizontal
        styles = getSampleStyleSheet()
        style_normal = styles["Normal"]
        style_title = ParagraphStyle(name="Title", parent=styles["Heading1"], fontSize=12, alignment=0)  # Alineación a la izquierda

        # Elementos del PDF
        elements = []

        # Añadir nombre y DNI en la parte superior izquierda
        elements.append(Paragraph(f"Nombre: {getattr(paciente, 'nombre', 'N/A')}", style_title))
        elements.append(Paragraph(f"DNI: {getattr(paciente, 'identificador', 'N/A')}", style_title))
        elements.append(Spacer(1, 10))

        # Insertar imagen del odontograma
        elements.append(ReportLabImage(img_path, width=700, height=350))  # Reducir ligeramente el tamaño

        # Finalizar el documento
        doc.build(elements)
        os.remove(img_path)  # Limpiar archivo temporal
        messagebox.showinfo("Éxito", f"Odontograma exportado a {file_path}")