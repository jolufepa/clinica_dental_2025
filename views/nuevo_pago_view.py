from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from models.pago import Pago
from services.database_service import DatabaseService

class NuevoPagoView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id
        self.title("Nuevo Pago")
        self.geometry("400x350")
        self._crear_formulario()
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _crear_formulario(self):
        ttk.Label(self, text="Monto Total:").pack(pady=5)
        self.entry_monto_total = ttk.Entry(self)
        self.entry_monto_total.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Monto Pagado:").pack(pady=5)
        self.entry_monto_pagado = ttk.Entry(self)
        self.entry_monto_pagado.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Método de Pago:").pack(pady=5)
        self.combo_metodo = ttk.Combobox(self, values=["Efectivo", "Tarjeta"])
        self.combo_metodo.pack(fill=tk.X, padx=10)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15)
        
        ttk.Button(frame_botones, text="Guardar", 
                 command=self._guardar_pago).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", 
                 command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _guardar_pago(self):
        try:
            monto_total = float(self.entry_monto_total.get())
            monto_pagado = float(self.entry_monto_pagado.get())
            metodo = self.combo_metodo.get().lower()
            saldo = monto_total - monto_pagado

            if saldo < 0:
                raise ValueError("El monto pagado no puede ser mayor al total")

            nuevo_pago = Pago(
                id_pago=None,
                id_visita=None,  # Puedes añadir lógica para vincular visitas
                identificador=self.paciente_id,
                monto_total=monto_total,
                monto_pagado=monto_pagado,
                fecha_pago=datetime.now().strftime("%Y-%m-%d"),
                metodo=metodo,
                saldo=saldo
            )

            db = DatabaseService()
            db.guardar_pago(nuevo_pago)
            messagebox.showinfo("Éxito", "Pago registrado correctamente")
            self.controller.actualizar_lista_pagos()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        finally:
            if 'db' in locals():
                db.cerrar_conexion()