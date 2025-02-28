# views/informes_view.py (modificado)
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
from services.database_service import DatabaseService
from models.cita import Cita
from models.visita import Visita
from models.pago import Pago
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from reportlab.lib.pagesizes import A4, landscape
from views.styles import configurar_estilos

class InformesView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.db = DatabaseService()
        self.title("Generar Informe - Clínica Dental P&D")
        self.geometry("600x500")
        self.resizable(True, True)

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

        # Calendarios
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(pady=10, fill=tk.X)

        ttk.Label(date_frame, text="Fecha Inicio:").grid(row=0, column=0, padx=5, pady=5)
        self.cal_inicio = Calendar(date_frame, selectmode="day", date_pattern="dd/mm/yyyy")
        self.cal_inicio.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(date_frame, text="Fecha Fin:").grid(row=1, column=0, padx=5, pady=5)
        self.cal_fin = Calendar(date_frame, selectmode="day", date_pattern="dd/mm/yyyy")
        self.cal_fin.grid(row=1, column=1, padx=5, pady=5)

        # Preajustes
        preset_frame = ttk.Frame(main_frame)
        preset_frame.pack(pady=5, fill=tk.X)
        ttk.Button(preset_frame, text="Hoy", command=self._set_hoy).grid(row=0, column=0, padx=5)
        ttk.Button(preset_frame, text="Últimos 10 días", command=self._set_ultimos_10_dias).grid(row=0, column=1, padx=5)

        # Desplegable de concepto
        ttk.Label(main_frame, text="Concepto:").pack(pady=5)
        self.concepto_var = tk.StringVar(value="citas")
        concepto_combo = ttk.Combobox(main_frame, textvariable=self.concepto_var, values=["citas", "visitas", "pagos"])
        concepto_combo.pack(pady=5)
        concepto_combo.bind("<<ComboboxSelected>>", self._toggle_paciente_filter)

        # Filtro por paciente
        self.paciente_var = tk.StringVar()
        paciente_frame = ttk.Frame(main_frame)
        paciente_frame.pack(pady=5, fill=tk.X)
        ttk.Label(paciente_frame, text="Paciente (Opcional):").grid(row=0, column=0, padx=5)
        self.paciente_combo = ttk.Combobox(paciente_frame, textvariable=self.paciente_var, width=30, postcommand=self._actualizar_pacientes, state="disabled")
        self.paciente_combo.grid(row=0, column=1, padx=5)
        self.paciente_combo.bind('<KeyRelease>', self._actualizar_pacientes)
        self._actualizar_pacientes()
        self._toggle_paciente_filter()  # Inicializar estado del filtro

        # Botón para generar vista previa
        ttk.Button(main_frame, text="Generar Vista Previa", command=self._mostrar_vista_previa).pack(pady=10)

    def _toggle_paciente_filter(self, event=None):
        if self.concepto_var.get() in ["citas", "visitas"]:
            self.paciente_combo.config(state="normal")
        else:
            self.paciente_combo.config(state="normal")
            self.paciente_var.set("")

    def _actualizar_pacientes(self, event=None):
        texto_busqueda = self.paciente_var.get().strip()
        if not texto_busqueda:
            self.paciente_combo['values'] = []
            return
        try:
            pacientes = self.controller.db.buscar_pacientes(texto_busqueda)
            sugerencias = [f"{p.identificador} - {p.nombre}" for p in pacientes]
            self.paciente_combo['values'] = sugerencias[:10]
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pacientes: {str(e)}")

    def _set_hoy(self):
        hoy = datetime.now().date()
        self.cal_inicio.selection_set(hoy.strftime("%d/%m/%Y"))
        self.cal_fin.selection_set(hoy.strftime("%d/%m/%Y"))
        self._mostrar_vista_previa()

    def _set_ultimos_10_dias(self):
        hoy = datetime.now().date()
        inicio = hoy - timedelta(days=10)
        self.cal_inicio.selection_set(inicio.strftime("%d/%m/%Y"))
        self.cal_fin.selection_set(hoy.strftime("%d/%m/%Y"))
        self._mostrar_vista_previa()

    def _mostrar_vista_previa(self):
        print("Generando vista previa...")  # Depuración
        fecha_inicio = datetime.strptime(self.cal_inicio.get_date(), "%d/%m/%Y").strftime("%Y-%m-%d")
        fecha_fin = datetime.strptime(self.cal_fin.get_date(), "%d/%m/%Y").strftime("%Y-%m-%d")
        print(f"Fechas: {fecha_inicio} a {fecha_fin}")  # Depuración
        if fecha_inicio > fecha_fin:
            messagebox.showerror("Error", "La fecha de inicio debe ser anterior o igual a la fecha de fin.")
            return

        concepto = self.concepto_var.get()
        paciente_id = None
        paciente_text = self.paciente_var.get().strip()
        if paciente_text and concepto in ["citas", "visitas"]:
            paciente_id = paciente_text.split(" - ")[0]

        try:
            registros = self.controller.db.obtener_registros_por_fecha(concepto, paciente_id, fecha_inicio, fecha_fin)
            print(f"Registros obtenidos: {len(registros)}")  # Depuración
            if not registros:
                messagebox.showwarning("Advertencia", "No se encontraron registros en el rango seleccionado.")
                return

            self._abrir_vista_previa(registros, concepto, fecha_inicio, fecha_fin)
        except Exception as e:
            print(f"Error en _mostrar_vista_previa: {str(e)}")  # Depuración
            messagebox.showerror("Error", f"Error al obtener datos: {str(e)}")

    def _abrir_vista_previa(self, registros, concepto, fecha_inicio, fecha_fin):
        vista = tk.Toplevel(self)
        vista.title("Vista Previa del Informe")
        vista.geometry("800x600")
        vista.resizable(True, True)

        # Treeview
        columns = {
            "citas": ("ID Cita", "Paciente", "DNI", "Fecha", "Hora", "Odontólogo", "Estado"),
            "visitas": ("ID Visita", "Paciente", "DNI", "Fecha", "Motivo", "Diagnóstico", "Tratamiento", "Odontólogo", "Estado"),
            "pagos": ("ID Pago", "Paciente", "DNI", "Fecha", "Monto Total", "Monto Pagado", "Método", "Saldo")
        }[concepto]
        tree = ttk.Treeview(vista, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100 if col in ["Estado", "Método"] else 120, anchor="center")
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Llenar Treeview
        for registro in registros:
            cita = Cita.from_tuple(registro[:-1]) if concepto == "citas" else None
            visita = Visita.from_tuple(registro[:-1]) if concepto == "visitas" else None
            pago = Pago.from_tuple(registro[:-1]) if concepto == "pagos" else None
            values = []
            nombre_paciente = registro[-1] if registro[-1] else "Desconocido"
            dni_mascarado = "*" * (len(registro[2]) - 4) + registro[2][-4:] if registro[2] else "N/A"  # Corregido a registro[2] para identificador
            if concepto == "citas":
                values = [cita.id_cita, nombre_paciente, dni_mascarado, cita.fecha, cita.hora, cita.odontologo, cita.estado]
            elif concepto == "visitas":
                values = [visita.id_visita, nombre_paciente, dni_mascarado, visita.fecha, visita.motivo, visita.diagnostico, visita.tratamiento, visita.odontologo, visita.estado]
            elif concepto == "pagos":
                values = [pago.id_pago, nombre_paciente, dni_mascarado, pago.fecha_pago, f"€{pago.monto_total:.2f}", f"€{pago.monto_pagado:.2f}", pago.metodo, f"€{pago.saldo:.2f}"]
            tree.insert("", "end", values=values)

        # Botones
        btn_frame = ttk.Frame(vista)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Generar PDF", command=lambda: self._generar_pdf(registros, concepto, fecha_inicio, fecha_fin, vista)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=vista.destroy).pack(side=tk.LEFT, padx=5)

    def _generar_pdf(self, registros, concepto, fecha_inicio, fecha_fin, vista):
        carpeta_anual = f"informes/{datetime.now().year}"
        mes_actual = datetime.now().strftime("%m")
        carpeta_mensual = f"{carpeta_anual}/{mes_actual}"
        os.makedirs(carpeta_mensual, exist_ok=True)

        timestamp = datetime.now().strftime("%H%M%S")
        paciente_nombre = self.paciente_var.get().split(" - ")[1] if self.paciente_var.get() else ""
        nombre_base = f"Informe_{concepto}_{paciente_nombre or str(registros[0][2]) if registros else concepto}_{timestamp}.pdf" if registros else f"Informe_{concepto}_{timestamp}.pdf"
        pdf_file = os.path.join(carpeta_mensual, nombre_base)

        # Determinar orientación basada en el número de columnas
        columns = {
            "citas": ("ID Cita", "Paciente", "DNI", "Fecha", "Hora", "Odontólogo", "Estado"),
            "visitas": ("ID Visita", "Paciente", "DNI", "Fecha", "Motivo", "Diagnóstico", "Tratamiento", "Odontólogo", "Estado"),
            "pagos": ("ID Pago", "Paciente", "DNI", "Fecha", "Monto Total", "Monto Pagado", "Método", "Saldo")
        }
        page_size = A4
        if len(columns[concepto]) > 6:  # Más de 6 columnas (ej. Pagos tiene 8)
            page_size = landscape(A4)

        # Crear el documento con SimpleDocTemplate
        c = canvas.Canvas(pdf_file, pagesize=page_size)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(inch, page_size[1] - inch, "Clínica Dental P&D")
        c.setFont("Helvetica", 10)
        c.drawString(inch, page_size[1] - 1.2 * inch, "Calle Ejemplo 123, Ciudad")
        c.drawString(inch, page_size[1] - 1.4 * inch, "Teléfono: 123-456-7890")
        c.drawString(inch, page_size[1] - 1.6 * inch, "Email: info@clinicadentalpd.com")

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(page_size[0] / 2, page_size[1] - 2 * inch, f"Informe - {concepto.capitalize()}")
        c.setFont("Helvetica", 10)
        c.drawString(inch, page_size[1] - 2.2 * inch, f"Rango: {datetime.strptime(fecha_inicio, '%Y-%m-%d').strftime('%d/%m/%Y')} a {datetime.strptime(fecha_fin, '%Y-%m-%d').strftime('%d/%m/%Y')}")

        y = page_size[1] - 2.5 * inch
        columns = columns[concepto]
        data = [columns]  # Encabezados como primera fila

        total = 0
        for registro in registros:
            cita = Cita.from_tuple(registro[:-1]) if concepto == "citas" else None
            visita = Visita.from_tuple(registro[:-1]) if concepto == "visitas" else None
            pago = Pago.from_tuple(registro[:-1]) if concepto == "pagos" else None
            dni_mascarado = "*" * (len(registro[2]) - 4) + registro[2][-4:] if registro[2] else "N/A"
            # Capitalizar el nombre del paciente
            nombre_paciente = registro[-1].title() if registro[-1] else "Desconocido"
            if concepto == "citas":
                row = [cita.id_cita, nombre_paciente, dni_mascarado, cita.fecha, cita.hora, cita.odontologo, cita.estado]
            elif concepto == "visitas":
                row = [visita.id_visita, nombre_paciente, dni_mascarado, visita.fecha, visita.motivo, visita.diagnostico, visita.tratamiento, visita.odontologo, visita.estado]
            elif concepto == "pagos":
                row = [pago.id_pago, nombre_paciente, dni_mascarado, pago.fecha_pago, f"€{pago.monto_total:.2f}", f"€{pago.monto_pagado:.2f}", pago.metodo, f"€{pago.saldo:.2f}"]
                total += registro[3]  # Sumar monto_pagado
            data.append(row)

        if concepto == "pagos":
            data.append(["", "", "", "", "", "", "Total:", f"€{total:.2f}"])

        # Crear tabla con bordes minimizados
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),  # Bordes sutiles
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        table_width = page_size[0] - 2 * inch  # Ancho total menos márgenes
        table.wrapOn(c, table_width, page_size[1])
        table.drawOn(c, inch, y - len(data) * 0.2 * inch)

        c.setFont("Helvetica", 8)
        c.drawString(inch, 0.5 * inch, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        c.showPage()
        c.save()

        vista.destroy()
        messagebox.showinfo("Éxito", f"Informe generado como '{pdf_file}' en la carpeta del proyecto.")

    def _cerrar_ventana(self):
        if 'informes' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['informes']
        self.destroy()