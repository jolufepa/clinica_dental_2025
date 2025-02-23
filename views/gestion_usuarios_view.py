import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService

class GestionUsuariosView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Gestión de Usuarios")
        self.geometry("600x400")
        self._crear_widgets()
        self._cargar_usuarios()
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _crear_widgets(self):
        # Frame superior con botones
        frame_superior = ttk.Frame(self)
        frame_superior.pack(pady=10, fill=tk.X)

        ttk.Button(frame_superior, text="Nuevo Usuario", 
                 command=self._nuevo_usuario).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ("Usuario", "Rol")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _cargar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            db = DatabaseService()
            usuarios = db.cursor.execute("SELECT username, role FROM usuarios").fetchall()
            
            for user in usuarios:
                self.tree.insert("", tk.END, values=user)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando usuarios: {str(e)}")
        finally:
            db.cerrar_conexion()

    def _nuevo_usuario(self):
        from views.nuevo_usuario_view import NuevoUsuarioView
        NuevoUsuarioView(self.controller)

    def actualizar_lista(self):
        self._cargar_usuarios()