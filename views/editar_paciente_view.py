# views/editar_paciente_view.py
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
        self.geometry("400x600")  # Aumentamos la altura para dar espacio a todos los campos
        self.resizable(True, True)  # Permitir redimensionar la ventana manualmente
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
        # Frame principal para organizar los widgets y permitir redimensionamiento
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Campos del formulario usando pack para un diseño flexible
        campos = [
            ("Identificador:", "entry_identificador", True),  # True indica readonly
            ("Nombre:", "entry_nombre", False),
            ("Teléfono:", "entry_telefono", False),
            ("Email:", "entry_email", False),
            ("Fecha Nacimiento (YYYY-MM-DD):", "entry_fecha_nac", False),
            ("Dirección:", "entry_direccion", False),
            ("Historial:", "text_historial", False),  # Usamos Text para historial
            ("Alergias:", "entry_alergias", False),
            ("Tratamientos previos:", "entry_tratamientos", False),
            ("Notas:", "entry_notas", False)
        ]

        for i, (texto, variable, readonly) in enumerate(campos):
            ttk.Label(main_frame, text=texto).pack(fill=tk.X, pady=2)
            if variable.startswith("text_"):  # Si es un Text
                widget = tk.Text(main_frame, height=3, width=40)
                widget.pack(fill=tk.X, padx=5, pady=2)
                setattr(self, variable, widget)
            else:  # Si es un Entry
                widget = ttk.Entry(main_frame, state='readonly' if readonly else 'normal')
                widget.pack(fill=tk.X, padx=5, pady=2)
                setattr(self, variable, widget)

        # Frame para los botones, alineado al final
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Guardar", command=self._guardar_cambios).pack(side=tk.LEFT, padx=5)

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
            self.text_historial.delete("1.0", tk.END)  # Corregido: usar text_historial y delete("1.0", tk.END)
            self.text_historial.insert("1.0", paciente.historial)  # Corregido: usar text_historial y insert("1.0", ...)
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
            self.destroy()
        except ValueError as ve:
            messagebox.showerror("Error", f"No se encontró el paciente: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar: {str(e)}")