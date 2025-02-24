# views/nueva_visita_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from models.visita import Visita

class NuevaVisitaView(tk.Toplevel):
    def __init__(self, controller, paciente_id):
        super().__init__()
        self.controller = controller
        self.paciente_id = str(paciente_id)
        self.title("Nueva Visita")
        self.geometry("500x400")
        self._crear_widgets()
        self.grab_set()  # Ventana modal

    def _crear_widgets(self):
        # Campo para mostrar el ID del paciente (no editable)
        ttk.Label(self, text="Paciente ID:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_paciente = ttk.Entry(self, state="readonly")
        self.entry_paciente.insert(0, self.paciente_id)  # Muestra el ID
        self.entry_paciente.grid(row=0, column=1, padx=5, pady=5)
        self.entry_paciente.configure(state="normal")
        
        self.entry_paciente.configure(state="readonly")

        # Resto de campos (fecha, motivo, diagnóstico, etc.)
        ttk.Label(self, text="Fecha (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_fecha = ttk.Entry(self)
        self.entry_fecha.grid(row=1, column=1, padx=5, pady=5)

        # Botón "Guardar Visita"
        ttk.Button(
            self, 
            text="Guardar Visita", 
            command=self._guardar_visita  # Vincula al método
        ).grid(row=5, column=0, columnspan=2, pady=20)

    # views/nueva_visita_view.py
    # Ejemplo en views/visitas_view.py
    def _abrir_nueva_visita(self):
        seleccion = self.tree.selection()
        if seleccion:
            paciente_id = self.tree.item(seleccion, "values")[0]  # Obtener ID del Treeview
            NuevaVisitaView(self.controller, paciente_id)
        else:
            messagebox.showwarning("Advertencia", "Seleccione un paciente primero")
    def _guardar_visita(self):
        if not self.paciente_id:  # Si no hay ID de paciente
            messagebox.showerror("Error", "No se ha asignado un paciente")
            return
        nueva_visita = Visita(
                identificador=self.paciente_id,
                fecha=self.entry_fecha.get(),
                motivo=self.entry_motivo.get(),
                diagnostico=self.entry_diagnostico.get(),
                tratamiento=self.entry_tratamiento.get(),
                odontologo=self.entry_odontologo.get(),
                estado="Pendiente"    
        )

        try:
            if self.controller.db.guardar_vista(nueva_visita):
                messagebox.showinfo("Éxito", "Visita registrada")
                self.controller.actualizar_lista_visitas()
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo guardar la visita")

        except Exception as e:
            error_msg = "Error: El paciente no existe" if "paciente no existe" in str(e) else f"Error: {str(e)}"
            messagebox.showerror("Error", error_msg)