# views/pacientes_view.py
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.paciente import Paciente
from views.nuevo_paciente_view import NuevoPacienteView
from views.editar_paciente_view import EditarPacienteView
import sys
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 


sys.path.append(str(Path(__file__).resolve().parent.parent))
class PacientesView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Gestión de Pacientes")
        self.geometry("800x600")
        self._crear_widgets()
        self._cargar_pacientes()  # Método correctamente definido
        self._centrar_ventana()
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = 800  # O self.winfo_width() después de crear widgets
        alto = 600   # O self.winfo_height() después de crear widgets
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

        # Treeview
        columns = ("Identificador", "Nombre", "Teléfono", "Email")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.W)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self._editar_paciente)
        
    def _seleccionar_paciente(self, event):
        seleccion = self.tree.selection()
        if seleccion:
            self.paciente_seleccionado = self.tree.item(seleccion, "values")[0]
            self.destroy()      
          

    def _cargar_pacientes(self):
        print("Controller.db:", self.controller.db)  # Depuración
        try:
            pacientes = self.controller.db.obtener_pacientes()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for p in pacientes:
                self.tree.insert("", "end", values=(
                    p.identificador,
                    p.nombre,
                    p.telefono,
                    p.email
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando pacientes: {str(e)}")

    def _buscar_pacientes(self, event=None):
        filtro = self.entry_busqueda.get().strip().lower()
        if not filtro:
            self._cargar_pacientes()
            return
        
        pacientes = self.controller.db.obtener_pacientes()
        pacientes_filtrados = [
            p for p in pacientes 
            if filtro in str(p.identificador).lower() or 
            filtro in p.nombre.lower() or 
            filtro in str(p.telefono).lower() or 
            filtro in p.email.lower()
        ]
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for p in pacientes_filtrados:
            self.tree.insert("", "end", values=(
                p.identificador,
                p.nombre,
                p.telefono,
                p.email
            ))
    # Ejemplo en pacientes_view.py al abrir visitas:
    def _abrir_visitas(self):
        seleccion = self.tree.selection()
        if seleccion:
            paciente_id = self.tree.item(seleccion, "values")[0]
            self.controller.mostrar_visitas(paciente_id)  # Pasa el ID
    def _nuevo_paciente(self):
        NuevoPacienteView(self.controller)
        self._cargar_pacientes()

    def _editar_paciente(self, event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un paciente")
            return
                    
        identificador = self.tree.item(seleccion)['values'][0]
        EditarPacienteView(self.controller, identificador)
        self._cargar_pacientes()
        
        
        

    def _eliminar_paciente(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un paciente")
            return
        
        identificador = self.tree.item(seleccion)['values'][0]
        if messagebox.askyesno("Confirmar", f"¿Eliminar paciente {identificador}?"):
            try:
                self.controller.db.eliminar_paciente(identificador)
                self._cargar_pacientes()
                messagebox.showinfo("Éxito", "Paciente eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {str(e)}")

    def _cerrar_ventana(self):
        if 'pacientes' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['pacientes']
        self.grab_release()
        self.destroy()