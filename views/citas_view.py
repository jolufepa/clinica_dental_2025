import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from services.database_service import DatabaseService
from models.cita import Cita

class CitasView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id
        self.title("Gestión de Citas")
        self.geometry("900x600")
        self._crear_widgets()
        self._cargar_citas()

    def _crear_widgets(self):
        # Frame superior
        frame_superior = ttk.Frame(self)
        frame_superior.pack(pady=10, fill=tk.X)

        ttk.Button(frame_superior, text="Nueva Cita", 
                 command=self._nueva_cita).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Fecha", "Hora", "Odontólogo", "Estado")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _cargar_citas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            db = DatabaseService()
            citas = db.obtener_citas(self.paciente_id)
            
            for c in citas:
                self.tree.insert("", tk.END, values=(
                    c.id_cita,
                    c.fecha,
                    c.hora,
                    c.odontologo,
                    c.estado.capitalize()
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando citas: {str(e)}")
        finally:
            db.cerrar_conexion()

    def _nueva_cita(self):
        from .nueva_cita_view import NuevaCitaView
        NuevaCitaView(self.controller, self.paciente_id)