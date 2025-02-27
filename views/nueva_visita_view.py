# ARCHIVO nueva_visita_view.py


from datetime import datetime
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from models.visita import Visita
from services.database_service import DatabaseService
from views.styles import configurar_estilos
from views.tooltip import ToolTip  # Importar la clase ToolTip

class NuevaVisitaView(tk.Toplevel):
    def __init__(self, controller, paciente_id):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id  # Almacenar el paciente_id recibido
        self.title("Nueva Visita")
        self.geometry("500x600")  # Tamaño suficiente para todos los campos
        self.resizable(True, True)  # Permitir redimensionar
        self._crear_formulario()
        configurar_estilos(self)  # Aplicar estilos globales
        self._centrar_ventana()
        self.lift()
        self.focus_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        self.destroy()

    def _crear_formulario(self):
        # Frame principal para organizar los widgets
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Campos del formulario usando pack para un diseño flexible
        campos = [
            ("Identificador del Paciente:", "entry_identificador", True),  # Readonly
            ("Fecha (DD/MM/YY):", "entry_fecha"),  # Cambiado de YYYY-MM-DD a DD/MM/YY
            ("Motivo:", "entry_motivo"),
            ("Diagnóstico:", "entry_diagnostico"),
            ("Tratamiento:", "entry_tratamiento"),
            ("Odontólogo:", "entry_odontologo"),
            ("Estado:", "entry_estado")
        ]

        for texto, variable, *extras in campos:
            readonly = extras[0] if extras else False  # Determinar si es readonly
            ttk.Label(main_frame, text=texto).pack(fill=tk.X, pady=5)
            entry = ttk.Entry(main_frame, state='readonly' if readonly else 'normal')
            entry.pack(fill=tk.X, padx=5, pady=2)
            if readonly and variable == "entry_identificador":
                entry.configure(state='normal')  # Temporalmente editable para insertar
                entry.insert(0, self.paciente_id or "")  # Insertar paciente_id recibido
                entry.configure(state='readonly')  # Volver a bloquear
            setattr(self, variable, entry)

        # Establecer valor predeterminado para "Estado"
        self.entry_estado.insert(0, "Pendiente")

        # Frame para los botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        guardar_btn = ttk.Button(button_frame, text="Guardar", command=self._guardar_visita)
        guardar_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(guardar_btn, "Guarda la nueva visita en la base de datos")  # Añadir tooltip

        cancelar_btn = ttk.Button(button_frame, text="Cancelar", command=self.destroy)
        cancelar_btn.pack(side=tk.LEFT, padx=5)
        ToolTip(cancelar_btn, "Cierra esta ventana sin guardar")  # Añadir tooltip

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _guardar_visita(self):
        identificador = self.entry_identificador.get().strip()
        fecha = self.entry_fecha.get().strip()
        motivo = self.entry_motivo.get().strip()
        diagnostico = self.entry_diagnostico.get().strip()
        tratamiento = self.entry_tratamiento.get().strip()
        odontologo = self.entry_odontologo.get().strip()
        estado = self.entry_estado.get().strip()

        if not all([identificador, fecha, motivo, odontologo, estado]):
            messagebox.showerror("Error", "Todos los campos obligatorios deben estar llenos")
            return

        try:
            # Validar y convertir fecha de DD/MM/YY a YYYY-MM-DD
            try:
                fecha_sql = datetime.strptime(fecha, "%d/%m/%y").strftime("%Y-%m-%d")
            except ValueError as ve:
                raise ValueError("Formato de fecha inválido. Usa DD/MM/YY (por ejemplo, 25/02/25)")

            nueva_visita = Visita(
                id_visita=None,  # ID se genera automáticamente en la base de datos
                identificador=identificador,
                fecha=fecha_sql,  # Usar el formato YYYY-MM-DD para la base de datos
                motivo=motivo,
                diagnostico=diagnostico,
                tratamiento=tratamiento,
                odontologo=odontologo,
                estado=estado
            )

            db = DatabaseService()
            if db.guardar_visita(nueva_visita):
                self.controller.actualizar_lista_visitas()
                messagebox.showinfo("Éxito", "Visita creada correctamente")
                self.destroy()
            else:
                messagebox.showerror("Error", "No se pudo crear la visita")
        except ValueError as ve:
            messagebox.showerror("Error", f"Formato de fecha inválido o datos inválidos: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")