# views/visitas_view.py
import tkinter as tk
from tkinter import ttk
from services.database_service import DatabaseService

class VisitasView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):  # Añadir parámetro opcional
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id  # Almacenar el ID si se proporciona
        self.title("Gestión de Visitas")
        self.geometry("1000x600")
        self._crear_widgets()
        self._cargar_visitas()
        self._cargar_pacientes()  # Cargar pacientes al iniciar

    def _crear_widgets(self):
        # Treeview para mostrar pacientes
        self.tree = ttk.Treeview(self, columns=("ID", "Nombre", "Teléfono"), show="headings")
        self.tree.heading("ID", text="Identificador")
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Teléfono", text="Teléfono")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Botón para crear nueva visita
        btn_nueva_visita = ttk.Button(
            self, 
            text="Nueva Visita", 
            command=self._abrir_nueva_visita
        )
        btn_nueva_visita.pack(pady=10)

    def _cargar_pacientes(self):
        """Obtiene y muestra los pacientes desde la base de datos"""
        try:
            pacientes = self.controller.db.obtener_pacientes()
            # Limpiar datos antiguos
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Insertar nuevos datos
            for paciente in pacientes:
                self.tree.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono
                ))
        except Exception as e:
            print(f"Error al cargar pacientes: {str(e)}")

    def _abrir_nueva_visita(self):
        """Abre la ventana de nueva visita con el paciente seleccionado"""
        seleccion = self.tree.selection()
        if seleccion:
            paciente_id = self.tree.item(seleccion, "values")[0]  # Obtener ID
            from views.nueva_visita_view import NuevaVisitaView
            NuevaVisitaView(self.controller, paciente_id)
        else:
            tk.messagebox.showwarning("Error", "Seleccione un paciente primero")