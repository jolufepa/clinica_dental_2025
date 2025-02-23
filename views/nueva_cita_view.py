import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from datetime import datetime
from models.cita import Cita
from services.database_service import DatabaseService

class NuevaCitaView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id
        self.title("Nueva Cita")
        self.geometry("400x450")
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
        ttk.Label(self, text="Fecha:").pack(pady=5)
        self.calendario = Calendar(self, selectmode='day', date_pattern='dd/mm/yyyy')
        self.calendario.pack(padx=10, pady=5)

        ttk.Label(self, text="Hora (HH:MM):").pack(pady=5)
        self.entry_hora = ttk.Entry(self)
        self.entry_hora.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Odontólogo:").pack(pady=5)
        self.entry_odontologo = ttk.Entry(self)
        self.entry_odontologo.pack(fill=tk.X, padx=10)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15)
        
        ttk.Button(frame_botones, text="Guardar", 
                 command=self._guardar_cita).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", 
                 command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _guardar_cita(self):
        try:
            fecha = self.calendario.get_date()
            hora = self.entry_hora.get()
            odontologo = self.entry_odontologo.get().strip()
            
            # Validar formato de hora
            datetime.strptime(hora, "%H:%M")
            
            nueva_cita = Cita(
                id_cita=None,
                identificador=self.paciente_id,
                fecha=fecha,
                hora=hora,
                odontologo=odontologo,
                estado="Programada"
            )

            db = DatabaseService()
            
            if not db.verificar_disponibilidad_cita(fecha, hora, odontologo):
                raise ValueError("El odontólogo no está disponible en ese horario")
                
            db.guardar_cita(nueva_cita)
            messagebox.showinfo("Éxito", "Cita programada correctamente")
            self.controller.actualizar_lista_citas()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        finally:
            if 'db' in locals():
                db.cerrar_conexion()