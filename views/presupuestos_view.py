# views/presupuestos_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from services.database_service import DatabaseService
from models.paciente import Paciente
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os

from views.styles import configurar_estilos

class PresupuestosView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Generar Presupuesto - Clínica Dental P&D")
        self.geometry("800x600")
        self.resizable(True, True)
        self.db = DatabaseService()
        self.concepto_rows = []

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

        # Buscador de pacientes
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Buscar Paciente (Opcional):").pack(side=tk.LEFT, padx=5)
        self.search_combo = ttk.Combobox(search_frame, width=30, postcommand=self._actualizar_sugerencias)
        self.search_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_combo.bind('<KeyRelease>', self._actualizar_sugerencias)
        self.search_combo.bind('<Return>', lambda event: self._seleccionar_paciente())
        self.search_combo.bind('<<ComboboxSelected>>', self._on_sugerencia_seleccionada)

        # Frame para los conceptos
        conceptos_frame = ttk.Frame(main_frame)
        conceptos_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Encabezados de la tabla de conceptos
        headers = ["Concepto", "Cantidad", "Monto/U (€)", "Monto Total (€)"]
        for i, header in enumerate(headers):
            ttk.Label(conceptos_frame, text=header, font=("Helvetica", 10, "bold"), width=20, anchor="center").grid(row=0, column=i, padx=5, pady=5)

        # Primera fila de conceptos
        self._agregar_fila_concepto(conceptos_frame, 1)

        # Botón para agregar más filas
        ttk.Button(main_frame, text="Agregar Concepto", command=lambda: self._agregar_fila_concepto(conceptos_frame, len(self.concepto_rows) + 1)).pack(pady=5)

        # Campo de observaciones
        ttk.Label(main_frame, text="Observaciones (Condiciones de Pago):").pack(pady=5)
        self.observaciones_text = tk.Text(main_frame, height=4, width=60)
        self.observaciones_text.pack(pady=5)

        # Botón para generar PDF
        ttk.Button(main_frame, text="Generar PDF", command=self._generar_pdf).pack(pady=10)

    def _actualizar_sugerencias(self, event=None):
        texto_busqueda = self.search_combo.get().strip()
        if not texto_busqueda:
            self.search_combo['values'] = []
            return
        try:
            pacientes = self.controller.db.buscar_pacientes(texto_busqueda)
            sugerencias = [f"{p.identificador} - {p.nombre}" for p in pacientes]
            self.search_combo['values'] = sugerencias[:10]
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar sugerencias: {str(e)}")

    def _on_sugerencia_seleccionada(self, event):
        seleccion = self.search_combo.get()
        if seleccion:
            identificador = seleccion.split(" - ")[0]
            self.search_combo.set(identificador)
            self._seleccionar_paciente()

    def _seleccionar_paciente(self):
        texto_busqueda = self.search_combo.get().strip()
        if texto_busqueda:
            paciente = self.controller.db.obtener_paciente(texto_busqueda)
            if paciente:
                messagebox.showinfo("Éxito", f"Paciente seleccionado: {paciente.nombre}")
            else:
                messagebox.showwarning("Advertencia", "Paciente no encontrado, puedes crear un presupuesto sin paciente.")

    def _agregar_fila_concepto(self, frame, row):
        concepto_var = tk.StringVar(value="Consulta")
        cantidad_var = tk.StringVar(value="1")
        monto_u_var = tk.StringVar(value="50.00")
        monto_total_var = tk.StringVar(value="€50.00")

        ttk.Combobox(frame, textvariable=concepto_var, values=["Consulta", "Limpieza", "Empaste", "Extracción"]).grid(row=row, column=0, padx=5, pady=5)
        ttk.Combobox(frame, textvariable=cantidad_var, values=[str(i) for i in range(1, 21)]).grid(row=row, column=1, padx=5, pady=5)
        monto_u_entry = ttk.Entry(frame, textvariable=monto_u_var, width=10)
        monto_u_entry.grid(row=row, column=2, padx=5, pady=5)
        ttk.Label(frame, textvariable=monto_total_var).grid(row=row, column=3, padx=5, pady=5)

        def actualizar_monto_total(*args):
            try:
                monto_u_str = monto_u_var.get().replace("€", "").strip()
                if not monto_u_str:
                    monto_u = 0.0
                else:
                    monto_u = float(monto_u_str)
                
                cantidad = int(cantidad_var.get())
                
                if cantidad < 1 or cantidad > 20:
                    raise ValueError("Cantidad debe estar entre 1 y 20")
                if monto_u < 0:
                    raise ValueError("Monto por unidad no puede ser negativo")
                
                monto_total = cantidad * monto_u
                monto_total_var.set(f"€{monto_total:.2f}")
            except ValueError as e:
                if monto_u_str and not monto_u_str.replace(".", "").isdigit():
                    messagebox.showerror("Error", "Monto por unidad debe ser un número válido.")
                elif str(e) != "Cantidad debe estar entre 1 y 20" and str(e) != "Monto por unidad no puede ser negativo":
                    messagebox.showerror("Error", f"Datos inválidos: {str(e)}")
                monto_total_var.set("€0.00")

        cantidad_var.trace_add('write', actualizar_monto_total)
        monto_u_var.trace_add('write', actualizar_monto_total)
        monto_u_entry.bind("<FocusOut>", lambda e: actualizar_monto_total())

        self.concepto_rows.append((concepto_var, cantidad_var, monto_u_var, monto_total_var))

    def _generar_pdf(self):
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        total_general = sum(float(row[3].get().replace("€", "").strip()) for row in self.concepto_rows if row[3].get().replace("€", "").strip())

        if not self.concepto_rows or total_general <= 0:
            messagebox.showerror("Error", "Debe haber al menos un concepto válido con monto positivo.")
            return

        # Obtener datos del paciente si se seleccionó
        texto_busqueda = self.search_combo.get().strip()
        datos_paciente = {
            "nombre": "",
            "identificacion": "",
            "telefono": ""
        }
        if texto_busqueda:
            paciente = self.controller.db.obtener_paciente(texto_busqueda)
            if paciente:
                datos_paciente = {
                    "nombre": paciente.nombre.title(),  # Convertir a mayúsculas iniciales
                    "identificacion": "*" * (len(paciente.identificador) - 4) + paciente.identificador[-4:],  # Mascarar DNI
                    "telefono": paciente.telefono
                }

        # Convertir las filas de conceptos a la estructura esperada
        procedimientos = []
        for concepto, cantidad, monto_u, monto_total in self.concepto_rows:
            monto_u_value = float(monto_u.get().replace("€", "").strip())
            monto_total_value = float(monto_total.get().replace("€", "").strip())
            procedimientos.append({
                "descripcion": concepto.get(),
                "cantidad": int(cantidad.get()),
                "precio_unitario": monto_u_value
            })

        # Datos de la clínica
        datos_clinica = {
            "nombre": "Clínica Dental P&D",
            "direccion": "Rambla Just Oliveras, 56 2 2 , L'Hospitalet",  # Ajusta según necesites
            "telefono": "933377714",  # Ajusta según necesites
            "email": "pddental22@gmail.com"  # Ajusta según necesites
        }

        # Obtener número correlativo
        ano_actual = datetime.now().year
        contador_file = "presupuesto_contador.txt"
        if os.path.exists(contador_file):
            with open(contador_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith(str(ano_actual)):
                        numero = int(line.split(":")[1].strip()) + 1
                        break
                else:
                    numero = 1
        else:
            numero = 1
        with open(contador_file, "w") as f:
            f.write(f"{ano_actual}:{numero}\n")

        # Título con número correlativo
        titulo = f"Presupuesto #{numero}"

        # Crear carpetas anual y mensual
        carpeta_anual = f"presupuestos/{ano_actual}"
        mes_actual = datetime.now().strftime("%m")
        carpeta_mensual = f"{carpeta_anual}/{mes_actual}"
        os.makedirs(carpeta_mensual, exist_ok=True)

        # Generar nombre de archivo único
        timestamp = datetime.now().strftime("%H%M%S")  # Hora, minuto, segundo (ej. 143022)
        nombre_base = datos_paciente['nombre'].replace(' ', '_') if datos_paciente['nombre'] else f"{numero}_Pres"
        nombre_archivo = f"{nombre_base}_{timestamp}.pdf"
        pdf_file = os.path.join(carpeta_mensual, nombre_archivo)

        # Observaciones como condiciones de pago
        condiciones_pago = self.observaciones_text.get("1.0", tk.END).strip() or "Efectivo, tarjeta de crédito"
        validez = "30 días"

        # Generar el PDF
        c = canvas.Canvas(pdf_file, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)

        # Encabezado
        c.drawString(inch, letter[1] - inch, datos_clinica["nombre"])
        c.setFont("Helvetica", 10)
        c.drawString(inch, letter[1] - 1.2 * inch, datos_clinica["direccion"])
        c.drawString(inch, letter[1] - 1.4 * inch, f"Teléfono: {datos_clinica['telefono']}")
        c.drawString(inch, letter[1] - 1.6 * inch, f"Email: {datos_clinica['email']}")

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(letter[0] / 2, letter[1] - 2 * inch, titulo)
        c.setFont("Helvetica", 10)
        c.drawRightString(letter[0] - inch, letter[1] - 2 * inch, f"Fecha: {fecha_actual}")

        # Datos del paciente
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, letter[1] - 3 * inch, "Datos del Paciente:")
        c.setFont("Helvetica", 10)
        c.drawString(inch, letter[1] - 3.2 * inch, f"Nombre: {datos_paciente['nombre']}")
        c.drawString(inch, letter[1] - 3.4 * inch, f"Identificación: {datos_paciente['identificacion']}")
        c.drawString(inch, letter[1] - 3.6 * inch, f"Teléfono: {datos_paciente['telefono']}")

        # Detalle de procedimientos
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, letter[1] - 4.2 * inch, "Detalle de Procedimientos:")
        y = letter[1] - 4.4 * inch
        c.setFont("Helvetica", 10)
        c.drawString(inch, y, "Procedimiento")
        c.drawString(3 * inch, y, "Cantidad")
        c.drawString(4 * inch, y, "Precio Unitario")
        c.drawString(5 * inch, y, "Precio Total")

        y -= 0.2 * inch
        c.line(inch, y, letter[0] - inch, y)  # Línea separadora

        y -= 0.2 * inch
        total = 0
        for procedimiento in procedimientos:
            c.drawString(inch, y, procedimiento["descripcion"])
            c.drawString(3 * inch, y, str(procedimiento["cantidad"]))
            c.drawString(4 * inch, y, f"€{procedimiento['precio_unitario']:.2f}")
            precio_total = procedimiento["cantidad"] * procedimiento['precio_unitario']
            c.drawString(5 * inch, y, f"€{precio_total:.2f}")
            total += precio_total
            y -= 0.2 * inch

        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(4 * inch, y - 0.4 * inch, "Total:")
        c.drawString(5 * inch, y - 0.4 * inch, f"€{total:.2f}")

        # Condiciones de pago
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y - 1 * inch, "Condiciones de Pago:")
        c.setFont("Helvetica", 10)
        c.drawString(inch, y - 1.2 * inch, condiciones_pago)

        # Validez
        c.setFont("Helvetica-Bold", 12)
        c.drawString(inch, y - 1.6 * inch, f"Validez: {validez}")

        # Firma
        c.setFont("Helvetica", 10)
        c.drawString(inch, y - 2 * inch, "Firma del Odontólogo:")
        c.line(4 * inch, y - 2 * inch, letter[0] - inch, y - 2 * inch)
        c.drawString(inch, y - 2.2 * inch, "Firma del Paciente:")
        c.line(4 * inch, y - 2.2 * inch, letter[0] - inch, y - 2.2 * inch)

        c.save()
        messagebox.showinfo("Éxito", f"Presupuesto generado como '{pdf_file}' en la carpeta del proyecto.")

    def _cerrar_ventana(self):
        if 'presupuestos' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['presupuestos']
        self.destroy()
        