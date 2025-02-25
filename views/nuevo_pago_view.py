# views/nuevo_pago_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.pago import Pago
from services.database_service import DatabaseService
from views.styles import configurar_estilos
class NuevoPagoView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__(controller.master)
        self.controller = controller
        self.paciente_id = paciente_id
        self.title("Nuevo Pago")
        self.geometry("400x500")
        self._crear_formulario()
        configurar_estilos(self)  # Aplicar estilos globales
        self._centrar_ventana()
        self.lift()
        self.focus_set()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _crear_formulario(self):
        # Campos para el nuevo pago
        ttk.Label(self, text="Paciente ID:").pack(pady=5)
        ttk.Label(self, text=f"{self.paciente_id}").pack(pady=5)  # Mostrar el paciente seleccionado

        ttk.Label(self, text="ID Visita (opcional):").pack(pady=5)
        self.entry_id_visita = ttk.Entry(self)
        self.entry_id_visita.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Monto Total (€):").pack(pady=5)
        self.entry_monto_total = ttk.Entry(self)
        self.entry_monto_total.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Monto Pagado (€):").pack(pady=5)
        self.entry_monto_pagado = ttk.Entry(self)
        self.entry_monto_pagado.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Fecha Pago (DD-MM-YYYY):").pack(pady=5)
        self.entry_fecha_pago = ttk.Entry(self)
        self.entry_fecha_pago.insert(0, datetime.now().strftime("%d-%m-%Y"))  # Fecha actual por defecto
        self.entry_fecha_pago.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Método de Pago:").pack(pady=5)
        self.entry_metodo = ttk.Entry(self)
        self.entry_metodo.pack(fill=tk.X, padx=10)

        # Botones
        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15)
        ttk.Button(frame_botones, text="Guardar", command=self._guardar_pago).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

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
            
            # Validar y parsear la fecha con manejo de errores
            try:
                # Intentar parsear la fecha en el formato esperado DD-MM-YYYY
                fecha_pago_obj = datetime.strptime(fecha_pago, "%d-%m-%Y")
                # Formatear la fecha de nuevo para asegurarnos de que sea consistente
                fecha_pago = fecha_pago_obj.strftime("%d-%m-%Y")
            except ValueError as e:
                # Si falla, intentar con otros formatos comunes o mostrar un mensaje claro
                try:
                    # Probar con DD/MM/YYYY (por si el usuario usa barras)
                    fecha_pago_obj = datetime.strptime(fecha_pago, "%d/%m/%Y")
                    fecha_pago = fecha_pago_obj.strftime("%d-%m-%Y")
                except ValueError:
                    raise ValueError("La fecha debe tener el formato DD-MM-YYYY o DD/MM-YYYY (por ejemplo, 25-02-2025)")

            # Calcular saldo
            saldo = monto_total - monto_pagado

            nuevo_pago = Pago(
                id_pago=None,  # Se genera automáticamente en la base de datos
                id_visita=id_visita,
                identificador=self.paciente_id,
                monto_total=monto_total,
                monto_pagado=monto_pagado,
                fecha_pago=fecha_pago,
                metodo=metodo,
                saldo=saldo
            )

            db = DatabaseService()
            if db.guardar_pago(nuevo_pago):
                messagebox.showinfo("Éxito", "Pago registrado correctamente")
                self.controller.actualizar_lista_pagos()  # Actualizar la lista en PagosView
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo registrar el pago")
        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar pago: {str(e)}")