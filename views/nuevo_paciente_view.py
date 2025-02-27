# CODIGO views/nuevo_paciente_view.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.paciente import Paciente
from services.database_service import DatabaseService
from views.styles import configurar_estilos

class NuevoPacienteView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Nuevo Paciente")
        self.geometry("600x700")  # Aumentamos el tamaño para mostrar todos los campos
        self.resizable(False, False)  # Evitar redimensionamiento manual
        self._crear_formulario()
        configurar_estilos(self)
        self._centrar_ventana()
        self.lift()
        self.focus_set()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_formulario(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sección Información Personal
        personal_frame = ttk.LabelFrame(main_frame, text="Información Personal", padding="10")
        personal_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        campos_personales = [
            ("Identificador (DNI/NIE):", "entry_identificador", tk.StringVar()),
            ("Nombre completo:", "entry_nombre", tk.StringVar()),
            ("Fecha nacimiento (DD/MM/AAAA):", "entry_fecha_nac", tk.StringVar()),
            ("Teléfono:", "entry_telefono", tk.StringVar()),
            ("Email:", "entry_email", tk.StringVar()),
            ("Dirección:", "entry_direccion", tk.StringVar())
        ]

        for i, (texto, variable, default) in enumerate(campos_personales):
            ttk.Label(personal_frame, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(personal_frame, textvariable=default, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            setattr(self, variable, entry)

        # Sección Historial Médico
        historial_frame = ttk.LabelFrame(main_frame, text="Historial Médico", padding="10")
        historial_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        campos_historial = [
            ("Alergias:", "entry_alergias", tk.StringVar()),
            ("Tratamientos previos:", "entry_tratamientos", tk.StringVar()),
            ("Notas:", "entry_notas", tk.StringVar()),
            ("Historial médico:", "text_historial", None)
        ]

        for i, (texto, variable, default) in enumerate(campos_historial):
            ttk.Label(historial_frame, text=texto).grid(row=i, column=0, padx=5, pady=5, sticky="e")
            if variable.startswith("text_"):
                widget = tk.Text(historial_frame, height=3, width=40)
                widget.grid(row=i, column=1, padx=5, pady=5, sticky="nsew")
                setattr(self, variable, widget)
            else:
                entry = ttk.Entry(historial_frame, textvariable=default, width=40)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                setattr(self, variable, entry)

        # Configurar expansión de filas y columnas
        personal_frame.grid_columnconfigure(1, weight=1)
        personal_frame.grid_rowconfigure(len(campos_personales) - 1, weight=1)
        historial_frame.grid_columnconfigure(1, weight=1)
        historial_frame.grid_rowconfigure(len(campos_historial) - 1, weight=1)

        # Botón de Guardar
        ttk.Button(main_frame, text="Guardar", command=self._guardar_paciente).pack(pady=15)

    def _guardar_paciente(self):
        try:
            identificador = self.entry_identificador.get().strip().upper()
            nombre = self.entry_nombre.get().strip()
            fecha_nac = self.entry_fecha_nac.get().strip()
            telefono = self.entry_telefono.get().strip()
            email = self.entry_email.get().strip()
            direccion = self.entry_direccion.get().strip()
            alergias = self.entry_alergias.get().strip()
            tratamientos = self.entry_tratamientos.get().strip()
            notas = self.entry_notas.get().strip()
            historial = self.text_historial.get("1.0", tk.END).strip()

            if not all([identificador, nombre, fecha_nac, telefono, email, direccion]):
                raise ValueError("Todos los campos obligatorios deben estar llenos")

            # Validar DNI/NIE
            if not self._validar_dni_nie(identificador):
                raise ValueError("DNI/NIE inválido. Formato esperado: 8 números + letra (DNI) o X/Y/Z + 7 números + letra (NIE)")

            # Validar formato de fecha (DD/MM/AAAA)
            try:
                datetime.strptime(fecha_nac, "%d/%m/%Y")
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use DD/MM/AAAA (por ejemplo, 25/02/2025)")

            nuevo_paciente = Paciente(
                identificador=identificador,
                nombre=nombre,
                fecha_nacimiento=fecha_nac,
                telefono=telefono,
                email=email,
                direccion=direccion,
                historial=historial,
                alergias=alergias,
                tratamientos_previos=tratamientos,
                notas=notas
            )

            db = DatabaseService()
            db.guardar_paciente(nuevo_paciente)  # Simplificamos, asumimos que lanza excepción si falla
            self.controller.actualizar_lista_pacientes()
            messagebox.showinfo("Éxito", "Paciente creado correctamente")
            self._on_close()
        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def _validar_dni_nie(self, identificador):
        # Validación básica de DNI/NIE (puedes expandirla)
        if len(identificador) == 9:
            if identificador[0:8].isdigit() and identificador[8].isalpha():
                return True  # DNI: 8 números + letra
            elif identificador[0] in 'XYZ' and identificador[1:8].isdigit() and identificador[8].isalpha():
                return True  # NIE: X/Y/Z + 7 números + letra
        return False       
   