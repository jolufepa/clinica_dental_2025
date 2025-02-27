import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.pago import Pago
from services.database_service import DatabaseService
from views.styles import configurar_estilos

class NuevoPagoView(tk.Toplevel):
    def __init__(self, controller, paciente_id):
        super().__init__(controller.master)
        self.controller = controller
        self.paciente_id = paciente_id  # Aseguramos que paciente_id no sea None
        self.title("Nuevo Pago")
        self.geometry("400x300")  # Reducido para consistencia
        self.resizable(True, True)  # Evitar redimensionamiento manual
        self._crear_formulario()
        configurar_estilos(self)  # Aplicar estilos globales
        self._centrar_ventana()
        self.lift()
        self.focus_set()
        self.grab_set()  # Hacer la ventana modal
        self.protocol("WM_DELETE_WINDOW", self._on_close)  # Añadir protocolo de cierre

    def _on_close(self):
        """Cierra la ventana liberando el grab y destruyéndola."""
        self.grab_release()
        self.destroy()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _crear_formulario(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Mostrar el paciente seleccionado (solo lectura, claro mensaje)
        ttk.Label(main_frame, text=f"Paciente: {self.paciente_id} (automático)").pack(pady=5)

        # Campos para el nuevo pago
        ttk.Label(main_frame, text="ID Visita (opcional):").pack(pady=5)
        self.entry_id_visita = ttk.Entry(main_frame)
        self.entry_id_visita.pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(main_frame, text="Monto Total (€):").pack(pady=5)
        self.entry_monto_total = ttk.Entry(main_frame)
        self.entry_monto_total.pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(main_frame, text="Monto Pagado (€):").pack(pady=5)
        self.entry_monto_pagado = ttk.Entry(main_frame)
        self.entry_monto_pagado.pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(main_frame, text="Fecha Pago (DD/MM/YY):").pack(pady=5)  # Cambiado de YYYY-MM-DD a DD/MM/YY
        # Insertar fecha actual en formato DD/MM/YY
        fecha_actual = datetime.now().strftime("%d/%m/%y")
        self.entry_fecha_pago = ttk.Entry(main_frame)
        self.entry_fecha_pago.insert(0, fecha_actual)
        self.entry_fecha_pago.pack(fill=tk.X, padx=10, pady=2)

        ttk.Label(main_frame, text="Método de Pago:").pack(pady=5)
        self.entry_metodo = ttk.Entry(main_frame)
        self.entry_metodo.pack(fill=tk.X, padx=10, pady=2)

        # Botones
        frame_botones = ttk.Frame(main_frame)
        frame_botones.pack(pady=10, fill=tk.X)
        ttk.Button(frame_botones, text="Guardar", command=self._guardar_pago).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self._on_close).pack(side=tk.LEFT, padx=5)

    def _guardar_pago(self):
        try:
            id_visita = self.entry_id_visita.get().strip() or None  # Opcional, puede ser None
            monto_total = float(self.entry_monto_total.get().strip())
            monto_pagado = float(self.entry_monto_pagado.get().strip())
            fecha_pago = self.entry_fecha_pago.get().strip()
            metodo = self.entry_metodo.get().strip()

            # Validar datos
            if not monto_total or not monto_pagado or not fecha_pago or not metodo:
                raise ValueError("Todos los campos son obligatorios (excepto ID Visita)")
            
            # Validar y convertir fecha de DD/MM/YY a YYYY-MM-DD
            try:
                fecha_pago_obj = datetime.strptime(fecha_pago, "%d/%m/%y")
                fecha_pago_sql = fecha_pago_obj.strftime("%Y-%m-%d")  # Formato para la base de datos
            except ValueError as ve:
                raise ValueError("Formato de fecha inválido. Usa DD/MM/YY (por ejemplo, 25/02/25)")

            # Validar que el monto pagado no exceda el monto total
            if monto_pagado > monto_total:
                raise ValueError("El monto pagado no puede exceder el monto total")

            # Calcular saldo
            saldo = monto_total - monto_pagado

            nuevo_pago = Pago(
                id_pago=None,  # Se genera automáticamente en la base de datos
                id_visita=id_visita,
                identificador=self.paciente_id,
                monto_total=monto_total,
                monto_pagado=monto_pagado,
                fecha_pago=fecha_pago_sql,  # Usar el formato YYYY-MM-DD para la base de datos
                metodo=metodo,
                saldo=saldo
            )

            db = DatabaseService()
            db.guardar_pago(nuevo_pago)  # Simplificamos, asumimos que lanza excepción si falla
            messagebox.showinfo("Éxito", "Pago registrado correctamente")
            self.controller.actualizar_lista_pagos()  # Actualizar la lista en PagosView y PacientesView
            self._on_close()  # Usar el método de cierre consistente
        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar pago: {str(e)}")