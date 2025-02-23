import tkinter as tk
from tkinter import ttk, messagebox
from models.paciente import Paciente
from services.database_service import DatabaseService

class NuevoPacienteView(tk.Toplevel):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.title("Nuevo Paciente")
        self.geometry("400x500")
        self.resizable(False, False)
        self._crear_formulario()
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _crear_formulario(self):
        campos = [
            ("Identificador (DNI/NIE):", "entry_identificador"),
            ("Nombre completo:", "entry_nombre"),
            ("Fecha nacimiento (DD/MM/AAAA):", "entry_fecha_nac"),
            ("Teléfono:", "entry_telefono"),
            ("Email:", "entry_email"),
            ("Dirección:", "entry_direccion")
        ]

        for texto, variable in campos:
            ttk.Label(self, text=texto).pack(pady=5)
            entry = ttk.Entry(self)
            entry.pack(fill=tk.X, padx=10)
            setattr(self, variable, entry)

        ttk.Label(self, text="Historial médico:").pack(pady=5)
        self.text_historial = tk.Text(self, height=5, width=40)
        self.text_historial.pack(padx=10, pady=5)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15)
        
        ttk.Button(frame_botones, text="Guardar", 
                 command=self._guardar_paciente).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", 
                 command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _guardar_paciente(self):
        datos = {
            'identificador': self.entry_identificador.get().strip().upper(),
            'nombre': self.entry_nombre.get().strip(),
            'fecha_nacimiento': self.entry_fecha_nac.get().strip(),
            'telefono': self.entry_telefono.get().strip(),
            'email': self.entry_email.get().strip(),
            'direccion': self.entry_direccion.get().strip(),
            'historial': self.text_historial.get("1.0", tk.END).strip()
        }

        try:
            nuevo_paciente = Paciente(**datos)
            db = DatabaseService()
            
            if db.existe_identificador(nuevo_paciente.identificador):
                messagebox.showerror("Error", "Este identificador ya está registrado")
                return
                
            db.guardar_paciente(nuevo_paciente)
            messagebox.showinfo("Éxito", "Paciente registrado correctamente")
            self.controller.actualizar_lista_pacientes()
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        finally:
            db.cerrar_conexion()