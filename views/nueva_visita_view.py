import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from models.visita import Visita

class NuevaVisitaView(tk.Toplevel):
    def __init__(self, controller, paciente_id):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id
        self.title("Nueva Visita")
        self.geometry("400x500")
        self._crear_formulario()

    def _crear_formulario(self):
        ttk.Label(self, text="Motivo:").pack(pady=5)
        self.motivo = ttk.Entry(self)
        self.motivo.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Fecha (YYYY-MM-DD):").pack(pady=5)
        self.fecha = ttk.Entry(self)
        self.fecha.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Odontólogo:").pack(pady=5)
        self.odontologo = ttk.Entry(self)
        self.odontologo.pack(fill=tk.X, padx=10)

        ttk.Button(self, text="Guardar", command=self._guardar).pack(pady=15)

    def _guardar(self):
        nueva_visita = Visita(
            id_visita=None,
            identificador=self.paciente_id,
            fecha=self.fecha.get(),
            motivo=self.motivo.get(),
            diagnostico="",  # Campos opcionales
            tratamiento="",
            odontologo=self.odontologo.get(),
            estado="Pendiente"
        )
        try:
            self.controller.db.guardar_visita(nueva_visita)
            self.destroy()
            self.controller.mostrar_visitas(self.paciente_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {str(e)}")