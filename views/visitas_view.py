import tkinter as tk
from tkinter import ttk, messagebox
from models.visita import Visita

class VisitasView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id
        self.title("Gestión de Visitas")
        self.geometry("800x600")
        self._crear_widgets()
        self._cargar_visitas()

    def _crear_widgets(self):
        # Frame superior
        frame_superior = ttk.Frame(self)
        frame_superior.pack(pady=10, fill=tk.X)

        ttk.Button(frame_superior, text="Nueva Visita", 
                 command=self._nueva_visita).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Fecha", "Motivo", "Odontólogo", "Estado")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _cargar_visitas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        visitas = self.controller.db.obtener_visitas(self.paciente_id)
        for v in visitas:
            self.tree.insert("", tk.END, values=(
                v.id_visita, v.fecha, v.motivo, 
                v.odontologo, v.estado
            ))

    def _nueva_visita(self):
        from views.nueva_visita_view import NuevaVisitaView
        NuevaVisitaView(self.controller, self.paciente_id)