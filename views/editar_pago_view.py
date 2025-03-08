# views/editar_pago_view.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from models.pago import Pago
from services.database_service import DatabaseService
from views.styles import configurar_estilos
from datetime import datetime

class EditarPagoView(tk.Toplevel):
    def __init__(self, controller, id_pago, paciente_id):
        super().__init__()
        self.controller = controller
        self.id_pago = id_pago
        self.paciente_id = paciente_id
        self.title("Editar Pago")
        self.geometry("400x300")
        self.resizable(False, False)
        self._crear_widgets()
        self._cargar_pago()
        configurar_estilos(self)
        self._centrar_ventana()
        self.lift()
        self.focus_set()
        self.grab_set()  # Ventana modal
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def _crear_widgets(self):
        # Frame principal para organizar los widgets
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Campos de edición
        campos = [
            ("ID Pago:", "entry_id_pago", True),  # Readonly
            ("Fecha (DD/MM/YY):", "entry_fecha", False),
            ("Monto Total (€):", "entry_monto_total", False),
            ("Monto Pagado (€):", "entry_monto_pagado", False),
            ("Método:", "combo_metodo", False),
            ("Saldo (€):", "entry_saldo", True)  # Readonly (se calcula automáticamente)
        ]

        for i, (texto, variable, readonly) in enumerate(campos):
            ttk.Label(main_frame, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if variable.startswith("combo_"):
                widget = ttk.Combobox(main_frame, values=["Efectivo", "Tarjeta", "Transferencia"], state='readonly' if readonly else 'normal', width=40)
                widget.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                setattr(self, variable, widget)
            else:
                entry = ttk.Entry(main_frame, state='readonly' if readonly else 'normal', width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                setattr(self, variable, entry)

        # Botón de Guardar
        ttk.Button(main_frame, text="Guardar", command=self._guardar_cambios).pack(pady=15)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _cargar_pago(self):
        print(f"Buscando pago con ID: {self.id_pago}")
        pago = self.controller.db.obtener_pago(self.id_pago)  # Asegúrate de que este método exista en DatabaseService
        if pago:
            self.entry_id_pago.configure(state='normal')
            self.entry_id_pago.delete(0, tk.END)
            self.entry_id_pago.insert(0, pago.id_pago)
            self.entry_id_pago.configure(state='readonly')

            fecha_europea = datetime.strptime(pago.fecha_pago, "%Y-%m-%d").strftime("%d/%m/%y")
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, fecha_europea)
            self.entry_monto_total.delete(0, tk.END)
            self.entry_monto_total.insert(0, f"{pago.monto_total:.2f}")
            self.entry_monto_pagado.delete(0, tk.END)
            self.entry_monto_pagado.insert(0, f"{pago.monto_pagado:.2f}")
            self.combo_metodo.set(pago.metodo)
            self.entry_saldo.configure(state='normal')
            self.entry_saldo.delete(0, tk.END)
            self.entry_saldo.insert(0, f"{pago.saldo:.2f}")
            self.entry_saldo.configure(state='readonly')
        else:
            messagebox.showerror("Error", f"Pago con ID {self.id_pago} no encontrado")
            self.destroy()

    def _guardar_cambios(self):
        nueva_fecha_europea = self.entry_fecha.get().strip()
        nuevo_monto_total = float(self.entry_monto_total.get().strip().replace('€', '').replace(',', '.'))
        nuevo_monto_pagado = float(self.entry_monto_pagado.get().strip().replace('€', '').replace(',', '.'))
        nuevo_metodo = self.combo_metodo.get()

        try:
            # Validar y convertir fecha
            nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
            if not all([nueva_fecha, nuevo_monto_total, nuevo_monto_pagado, nuevo_metodo]):
                raise ValueError("Todos los campos son obligatorios")

            # Calcular nuevo saldo
            nuevo_saldo = nuevo_monto_total - nuevo_monto_pagado

            # Crear nuevo objeto Pago
            pago = Pago(self.id_pago, None, self.paciente_id, nuevo_monto_total, nuevo_monto_pagado, nueva_fecha, nuevo_metodo, nuevo_saldo)
            self.controller.db.actualizar_pago(pago)
            self.controller.actualizar_lista_pagos()  # Asegúrate de que este método esté en MainController
            messagebox.showinfo("Éxito", "Pago actualizado correctamente")
            self._on_close()
        except ValueError as ve:
            messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el pago: {str(e)}")