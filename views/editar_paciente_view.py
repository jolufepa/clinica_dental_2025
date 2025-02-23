import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from models.paciente import Paciente

class EditarPacienteView(tk.Toplevel):
    def __init__(self, controller, identificador):
        super().__init__()
        self.controller = controller
        self.identificador = identificador
        self.title("Editar Paciente")
        self.geometry("400x300")
        self._crear_widgets()
        self._cargar_paciente()
        self.focus_set()  # Asegura que la ventana reciba focus

    def _crear_widgets(self):
        # Configurar estilos (opcional, pero asegúrate de definir 'estilo' si lo usas)
        estilo = ttk.Style()  # Definir estilo aquí si lo necesitas
        estilo.theme_use('clam')  # Usar el tema 'clam' como en MainController

        # Crear campos para editar, asegurándonos de que sean editables por defecto
        ttk.Label(self, text="Identificador:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_identificador = ttk.Entry(self, state='normal')  # Explicitamente 'normal' para editable
        self.entry_identificador.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Nombre:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_nombre = ttk.Entry(self, state='normal')  # Explicitamente 'normal' para editable
        self.entry_nombre.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self, text="Teléfono:").grid(row=2, column=0, padx=5, pady=5)
        self.entry_telefono = ttk.Entry(self, state='normal')  # Explicitamente 'normal' para editable
        self.entry_telefono.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self, text="Email:").grid(row=3, column=0, padx=5, pady=5)
        self.entry_email = ttk.Entry(self, state='normal')  # Explicitamente 'normal' para editable
        self.entry_email.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self, text="Guardar", command=self._guardar_cambios).grid(row=4, column=0, columnspan=2, pady=10)

    def _cargar_paciente(self):
        print("Controller.db en _cargar_paciente:", self.controller.db)  # Depuración
        paciente = self.controller.db.obtener_paciente(self.identificador)
        if paciente:
            self.entry_identificador.delete(0, tk.END)  # Limpia y añade los datos
            self.entry_identificador.insert(0, paciente.identificador)
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, paciente.nombre)
            self.entry_telefono.delete(0, tk.END)
            self.entry_telefono.insert(0, paciente.telefono)
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, paciente.email)
        else:
            messagebox.showerror("Error", "Paciente no encontrado")

    def _guardar_cambios(self):
        nuevo_paciente = Paciente(
            self.entry_identificador.get(),
            self.entry_nombre.get(),
            "",  # fecha_nacimiento (puedes añadir un campo si es necesario)
            self.entry_telefono.get(),
            self.entry_email.get(),
            "",  # direccion (puedes añadir un campo si es necesario)
            ""   # historial (puedes añadir un campo si es necesario)
        )
        try:
            self.controller.db.actualizar_paciente(nuevo_paciente)
            messagebox.showinfo("Éxito", "Paciente actualizado")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")