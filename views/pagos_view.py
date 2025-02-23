import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.pago import Pago

class PagosView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id
        self.title("Gestión de Pagos")
        self.geometry("800x600")
        self._crear_widgets()
        self._cargar_pagos()

    def _crear_widgets(self):
        # Frame superior
        frame_superior = ttk.Frame(self)
        frame_superior.pack(pady=10, fill=tk.X)

        ttk.Button(frame_superior, text="Nuevo Pago", 
                 command=self._nuevo_pago).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Fecha", "Monto Total", "Pagado", "Método", "Saldo")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _cargar_pagos(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            db = DatabaseService()
            pagos = db.obtener_pagos(self.paciente_id)
            
            for p in pagos:
                self.tree.insert("", tk.END, values=(
                    p.id_pago,
                    p.fecha_pago,
                    f"€{p.monto_total:.2f}",
                    f"€{p.monto_pagado:.2f}",
                    p.metodo.capitalize(),
                    f"€{p.saldo:.2f}"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando pagos: {str(e)}")
        finally:
            db.cerrar_conexion()

    def _nuevo_pago(self):
        from views.nuevo_pago_view import NuevoPagoView
        NuevoPagoView(self.controller, self.paciente_id)