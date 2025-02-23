import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService

class NuevoUsuarioView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Nuevo Usuario")
        self.geometry("300x200")
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
        ttk.Label(self, text="Usuario:").pack(pady=5)
        self.entry_usuario = ttk.Entry(self)
        self.entry_usuario.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Contraseña:").pack(pady=5)
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Rol:").pack(pady=5)
        self.combo_rol = ttk.Combobox(self, values=["admin", "recepcion"])
        self.combo_rol.pack(fill=tk.X, padx=10)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15)
        
        ttk.Button(frame_botones, text="Guardar", 
                 command=self._guardar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", 
                 command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _guardar_usuario(self):
        try:
            username = self.entry_usuario.get().strip()
            password = self.entry_password.get().strip()
            role = self.combo_rol.get().lower()

            if not all([username, password, role]):
                raise ValueError("Todos los campos son obligatorios")

            if role not in ["admin", "recepcion"]:
                raise ValueError("Rol inválido")

            db = DatabaseService()
            
            if db.cursor.execute("SELECT username FROM usuarios WHERE username = ?", 
                               (username,)).fetchone():
                raise ValueError("El usuario ya existe")
                
            db.crear_usuario(username, password, role)
            messagebox.showinfo("Éxito", "Usuario creado correctamente")
            self.controller.usuarios_view.actualizar_lista()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
        finally:
            db.cerrar_conexion()