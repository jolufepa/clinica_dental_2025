# views/editar_visita_view.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from models.visita import Visita
from services.database_service import DatabaseService
from views.styles import configurar_estilos
from datetime import datetime

class EditarVisitaView(tk.Toplevel):
    def __init__(self, controller, id_visita, paciente_id):
        super().__init__()
        self.controller = controller
        self.id_visita = id_visita
        self.paciente_id = paciente_id
        self.title("Editar Visita")
        self.geometry("500x400")
        self.resizable(False, False)
        self._crear_widgets()
        self._cargar_visita()
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
            ("ID Visita:", "entry_id_visita", True),
            ("Fecha (DD/MM/YY):", "entry_fecha", False),
            ("Motivo:", "entry_motivo", False),
            ("Diagnóstico:", "entry_diagnostico", False),
            ("Tratamiento:", "entry_tratamiento", False),
            ("Odontólogo:", "entry_odontologo", False),
            ("Estado:", "combo_estado", False)
        ]

        for i, (texto, variable, readonly) in enumerate(campos):
            ttk.Label(main_frame, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if variable.startswith("combo_"):
                widget = ttk.Combobox(main_frame, values=["Pendiente", "Completada", "Cancelada"], state='readonly' if readonly else 'normal', width=40)
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

    def _cargar_visita(self):
        print(f"Buscando visita con ID: {self.id_visita}")
        visita = self.controller.db.obtener_visita(self.id_visita)  # Asegúrate de que este método exista
        if visita:
            self.entry_id_visita.configure(state='normal')
            self.entry_id_visita.delete(0, tk.END)
            self.entry_id_visita.insert(0, visita.id_visita)
            self.entry_id_visita.configure(state='readonly')

            # Convertir de YYYY-MM-DD a DD/MM/YY
            fecha_europea = datetime.strptime(visita.fecha, "%Y-%m-%d").strftime("%d/%m/%y")
            self.entry_fecha.delete(0, tk.END)
            self.entry_fecha.insert(0, fecha_europea)
            self.entry_motivo.delete(0, tk.END)
            self.entry_motivo.insert(0, visita.motivo)
            self.entry_diagnostico.delete(0, tk.END)
            self.entry_diagnostico.insert(0, visita.diagnostico)
            self.entry_tratamiento.delete(0, tk.END)
            self.entry_tratamiento.insert(0, visita.tratamiento)
            self.entry_odontologo.delete(0, tk.END)
            self.entry_odontologo.insert(0, visita.odontologo)
            self.combo_estado.set(visita.estado)
        else:
            messagebox.showerror("Error", f"Visita con ID {self.id_visita} no encontrada")
            self.destroy()

    def _guardar_cambios(self):
        nueva_fecha_europea = self.entry_fecha.get().strip()
        print(f"Guardando fecha: {nueva_fecha_europea}")  # Depuración
        nuevo_motivo = self.entry_motivo.get().strip()
        nuevo_diagnostico = self.entry_diagnostico.get().strip()
        nuevo_tratamiento = self.entry_tratamiento.get().strip()
        nuevo_odontologo = self.entry_odontologo.get().strip()
        nuevo_estado = self.combo_estado.get()

        try:
            nueva_fecha = datetime.strptime(nueva_fecha_europea, "%d/%m/%y").strftime("%Y-%m-%d")
            if not all([nueva_fecha, nuevo_motivo, nuevo_odontologo, nuevo_estado]):
                raise ValueError("Todos los campos son obligatorios")

            visita = Visita(self.id_visita, self.paciente_id, nueva_fecha, nuevo_motivo, nuevo_diagnostico, nuevo_tratamiento, nuevo_odontologo, nuevo_estado)
            self.controller.db.actualizar_visita(visita)
            self.controller.actualizar_lista_visitas()
            messagebox.showinfo("Éxito", "Visita actualizada correctamente")
            self._on_close()
        except ValueError as ve:
            messagebox.showerror("Error", f"Datos inválidos: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar la visita: {str(e)}")