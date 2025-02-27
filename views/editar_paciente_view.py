# ARCHIVO views/editar_paciente_view.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from models.paciente import Paciente
from services.database_service import DatabaseService
from views.styles import configurar_estilos

class EditarPacienteView(tk.Toplevel):
    def __init__(self, controller, identificador):
        super().__init__()
        self.controller = controller
        self.identificador = identificador
        self.title("Editar Paciente")
        self.geometry("600x700")  # Aumentamos el tamaño para mostrar todos los campos
        self.resizable(False, False)  # Evitar redimensionamiento manual
        self._crear_widgets()
        configurar_estilos(self)  # Aplicar estilos globales
        self._cargar_paciente()
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

        # Sección Información Personal
        personal_frame = ttk.LabelFrame(main_frame, text="Información Personal", padding="10")
        personal_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        campos_personales = [
            ("DNI/NIF/NIE:", "entry_identificador", True),  # Readonly
            ("Nombre:", "entry_nombre", False),
            ("Teléfono:", "entry_telefono", False),
            ("Email:", "entry_email", False),
            ("Fecha Nacimiento (DD/MM/AAAA):", "entry_fecha_nac", False),
            ("Dirección:", "entry_direccion", False)
        ]

        for i, (texto, variable, readonly) in enumerate(campos_personales):
            ttk.Label(personal_frame, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(personal_frame, state='readonly' if readonly else 'normal', width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            setattr(self, variable, entry)

        # Sección Historial Médico
        historial_frame = ttk.LabelFrame(main_frame, text="Historial Médico", padding="10")
        historial_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        campos_historial = [
            ("Historial:", "text_historial", False),
            ("Alergias:", "entry_alergias", False),
            ("Tratamientos previos:", "entry_tratamientos", False),
            ("Notas:", "entry_notas", False)
        ]

        for i, (texto, variable, readonly) in enumerate(campos_historial):
            ttk.Label(historial_frame, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if variable.startswith("text_"):
                widget = tk.Text(historial_frame, height=3, width=40)
                widget.grid(row=i, column=1, padx=5, pady=5, sticky="nsew")
                setattr(self, variable, widget)
            else:
                entry = ttk.Entry(historial_frame, state='normal', width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                setattr(self, variable, entry)

        # Configurar expansión de filas y columnas
        personal_frame.grid_columnconfigure(1, weight=1)
        personal_frame.grid_rowconfigure(len(campos_personales) - 1, weight=1)
        historial_frame.grid_columnconfigure(1, weight=1)
        historial_frame.grid_rowconfigure(len(campos_historial) - 1, weight=1)

        # Botón de Guardar
        ttk.Button(main_frame, text="Guardar", command=self._guardar_cambios).pack(pady=15)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _cargar_paciente(self):
        print(f"Buscando paciente con identificador: {self.identificador}")
        paciente = self.controller.db.obtener_paciente(self.identificador)
        if paciente:
            self.entry_identificador.configure(state='normal')
            self.entry_identificador.delete(0, tk.END)
            self.entry_identificador.insert(0, paciente.identificador)
            self.entry_identificador.configure(state='readonly')
            
            self.entry_nombre.delete(0, tk.END)
            self.entry_nombre.insert(0, paciente.nombre)
            self.entry_telefono.delete(0, tk.END)
            self.entry_telefono.insert(0, paciente.telefono)
            self.entry_email.delete(0, tk.END)
            self.entry_email.insert(0, paciente.email)
            self.entry_fecha_nac.delete(0, tk.END)
            self.entry_fecha_nac.insert(0, paciente.fecha_nacimiento)
            self.entry_direccion.delete(0, tk.END)
            self.entry_direccion.insert(0, paciente.direccion)
            self.text_historial.delete("1.0", tk.END)
            self.text_historial.insert("1.0", paciente.historial)
            self.entry_alergias.delete(0, tk.END)
            self.entry_alergias.insert(0, paciente.alergias)
            self.entry_tratamientos.delete(0, tk.END)
            self.entry_tratamientos.insert(0, paciente.tratamientos_previos)
            self.entry_notas.delete(0, tk.END)
            self.entry_notas.insert(0, paciente.notas)
        else:
            messagebox.showerror("Error", f"Paciente con identificador {self.identificador} no encontrado")
            self.destroy()

    def _guardar_cambios(self):
        nuevo_paciente = Paciente(
            self.entry_identificador.get().strip().upper(),
            self.entry_nombre.get().strip(),
            self.entry_fecha_nac.get().strip(),
            self.entry_telefono.get().strip(),
            self.entry_email.get().strip(),
            self.entry_direccion.get().strip(),
            self.text_historial.get("1.0", tk.END).strip(),
            self.entry_alergias.get().strip(),
            self.entry_tratamientos.get().strip(),
            self.entry_notas.get().strip()
        )
        try:
            self.controller.db.actualizar_paciente(nuevo_paciente)
            self.controller.actualizar_lista_pacientes()
            messagebox.showinfo("Éxito", "Paciente actualizado correctamente")
            self._on_close()
        except ValueError as ve:
            messagebox.showerror("Error", f"No se encontró el paciente: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")