# views/pacientes_view.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.paciente import Paciente
from views.nuevo_paciente_view import NuevoPacienteView
from views.editar_paciente_view import EditarPacienteView
from views.styles import configurar_estilos

class PacientesView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Gestión de Pacientes")
        self.geometry("800x600")
        self._crear_widgets()
        self._cargar_pacientes()
        self._centrar_ventana()
        configurar_estilos(self)  # Llamar a la función centralizada
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 800
        alto = 600
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_widgets(self):
        # Frame superior con botones
        frame_superior = ttk.Frame(self)
        frame_superior.pack(pady=10, fill=tk.X)

        ttk.Button(frame_superior, text="Nuevo Paciente", 
                   command=self._nuevo_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_superior, text="Editar", 
                   command=self._editar_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_superior, text="Eliminar", 
                   command=self._eliminar_paciente).pack(side=tk.LEFT, padx=5)

        # Barra de búsqueda
        self.entry_busqueda = ttk.Entry(frame_superior)
        self.entry_busqueda.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)
        ttk.Button(frame_superior, text="Buscar", 
                   command=self._buscar_pacientes).pack(side=tk.RIGHT, padx=5)

        # Treeview con columnas actualizadas
        columns = ("Identificador", "Nombre", "Teléfono", "Email", "Dirección", "Historial", "Alergias", "Tratamientos previos", "Notas")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150 if col != "Historial" and col != "Notas" else 200, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self._editar_paciente)

    def _cargar_pacientes(self):
        """Obtiene y muestra todos los pacientes desde la base de datos"""
        try:
            pacientes = self.controller.db.obtener_pacientes()
            print(f"Pacientes obtenidos: {[p.__dict__ for p in pacientes]}")  # Depuración
            for item in self.tree.get_children():
                self.tree.delete(item)
            for paciente in pacientes:
                self.tree.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono,
                    paciente.email,
                    paciente.direccion,
                    paciente.historial,
                    paciente.alergias,
                    paciente.tratamientos_previos,
                    paciente.notas
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando pacientes: {str(e)}")

    def _buscar_pacientes(self):
        """Busca pacientes por nombre o identificador"""
        texto_busqueda = self.entry_busqueda.get().strip().upper()
        try:
            pacientes = self.controller.db.buscar_pacientes(texto_busqueda)
            for item in self.tree.get_children():
                self.tree.delete(item)
            for paciente in pacientes:
                self.tree.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono,
                    paciente.email,
                    paciente.direccion,
                    paciente.historial,
                    paciente.alergias,
                    paciente.tratamientos_previos,
                    paciente.notas
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error buscando pacientes: {str(e)}")

    def _nuevo_paciente(self):
        NuevoPacienteView(self.controller)

    def _editar_paciente(self, event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un paciente")
            return
        
        identificador = self.tree.item(seleccion)['values'][0]
        EditarPacienteView(self.controller, identificador)
        self._cargar_pacientes()  # Actualizar la lista después de editar

    def _eliminar_paciente(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un paciente")
            return
        
        identificador = self.tree.item(seleccion)['values'][0]
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este paciente?"):
            try:
                self.controller.db.eliminar_paciente(identificador)
                self._cargar_pacientes()
                messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar paciente: {str(e)}")

    def _cerrar_ventana(self):
        if 'pacientes' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['pacientes']
        self.destroy()