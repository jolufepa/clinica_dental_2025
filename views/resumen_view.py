# views/resumen_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from views.styles import configurar_estilos
from datetime import datetime

class ResumenView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Resumen de la Clínica")
        self.geometry("600x400")
        self._crear_widgets()
        configurar_estilos(self)
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Obtener datos de la base de datos
        db = self.controller.db
        try:
            # Contar pacientes activos
            pacientes = db.obtener_pacientes()
            num_pacientes = len(pacientes)

            # Sumar pagos del mes actual (febrero 2025)
            mes_actual = datetime.now().strftime("%Y-%m")
            pagos = db.obtener_pagos_mes(mes_actual)  # Usar el método propuesto en DatabaseService
            total_pagos = sum(pago.monto_pagado for pago in pagos if pago.monto_pagado is not None)

            # Mostrar estadísticas
            ttk.Label(main_frame, text=f"Número de pacientes: {num_pacientes}", font=("Helvetica", 12)).pack(pady=10)
            ttk.Label(main_frame, text=f"Total pagos del mes (Feb 2025): €{total_pagos:.2f}", font=("Helvetica", 12)).pack(pady=10)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los datos del resumen: {str(e)}")

    def destroy(self):
        super().destroy()