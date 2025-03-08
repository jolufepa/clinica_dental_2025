# views/editar_cita_view.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from models.cita import Cita
from services.database_service import DatabaseService
from views.styles import configurar_estilos
from datetime import datetime

class EditarCitaView(tk.Toplevel):
    def __init__(self, controller, id_cita, paciente_id):
        super().__init__()
        self.controller = controller
        self.id_cita = id_cita
        self.paciente_id = paciente_id
        self.title("Editar Cita")
        self.geometry("400x300")
        self.resizable(False, False)
        self._crear_widgets()
        self._cargar_cita()
        configurar_estilos(self)
        self._centrar_ventana()
        self.lift()
        self.focus_set()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def _crear_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        campos = [
            ("ID Cita:", "entry_id_cita", True),
            ("Fecha (DD/MM/YY):", "entry_fecha", False),
            ("Hora (HH:MM):", "entry_hora", False),
            ("Odontólogo:", "entry_odontologo", False),
            ("Estado:", "combo_estado", False)
        ]

        for i, (texto, variable, readonly) in enumerate(campos):
            ttk.Label(main_frame, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if variable.startswith("combo_"):
                widget = ttk.Combobox(main_frame, values=["Pendiente", "Confirmada", "Cancelada", "Completada"], state='readonly' if readonly else 'normal', width=40)
                widget.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                setattr(self, variable, widget)
            else:
                entry = ttk.Entry(main_frame, state='readonly' if readonly else 'normal', width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                setattr(self, variable, entry)

        ttk.Button(main_frame, text="Guardar", command=self._guardar_cambios).pack(pady=15)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _cargar_cita(self):
        print(f"Buscando cita con ID: {self.id_cita}")
        cita = self.controller.db.obtener_cita(self.id_cita)  # Asegúrate de que este método exista en DatabaseService
        if cita:
            self.entry_id_cita.configure(state='normal')
            self.entry_id_cita.delete(0, tk.END)
            self.entry_id_cita.insert(0, cita.id_cita)
            self.entry_id_cita.configure(state='readonly')

            fecha_europea = datetime.strptime(cita.fecha, "%Y-%m-%d").strftime("%d/%m/%y")
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, fecha_europea)
            self.entry_hora.delete(0, tk.END)
            self.entry_hora.insert(0, cita.hora)
            self.entry_odontologo.delete(0, tk.END)
            self.entry_odontologo.insert(0, cita.odontologo)
            self.combo_estado.set(cita.estado)
        else:
            messagebox.showerror("Error", f"Cita con ID {self.id_cita} no encontrada")
            self.destroy()

    def _guardar_cambios(self):
        nueva_fecha_europea = self.entry_fecha.get().strip()
        nueva_hora = self.entry_hora.get().strip()
        nuevo_odontologo = self.entry_odontologo.get().strip()
        nuevo_estado = self.combo_estado.get()

        try:
            # Validar y convertir fecha
            nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
            if not all([nueva_fecha, nueva_hora, nuevo_odontologo, nuevo_estado]):
                raise ValueError("Todos los campos son obligatorios")

            cita = Cita(self.id_cita, self.paciente_id, nueva_fecha, nueva_hora, nuevo_odontologo, nuevo_estado)
            self.controller.db.actualizar_cita(cita)
            self.controller.actualizar_lista_citas()  # Asegúrate de que este método esté en MainController
            messagebox.showinfo("Éxito", "Cita actualizada correctamente")
            self._on_close()
        except ValueError as ve:
            messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la cita: {str(e)}")