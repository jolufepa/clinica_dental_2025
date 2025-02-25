# views/gestion_usuarios_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from views.styles import configurar_estilos
class GestionUsuariosView(tk.Toplevel):
    def __init__(self, controller):
        super().__init__(controller.master)  # Usar master del controller para mantener jerarquía
        self.controller = controller
        self.title("Gestión de Usuarios")
        self.geometry("600x400")
        self._crear_widgets()
        configurar_estilos(self)  # Aplicar estilos globales
        self._cargar_usuarios()
        self._centrar_ventana()
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)  # Gestionar cierre

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
        ttk.Button(frame_superior, text="Editar Usuario", 
                   command=self._editar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_superior, text="Eliminar Usuario", 
                   command=self._eliminar_usuario).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ("Usuario", "Rol")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Vincular selección en Treeview para acciones
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _cargar_usuarios(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            db = DatabaseService()  # Usar Singleton, no cerrar aquí
            usuarios = db.cursor.execute("SELECT username, role FROM usuarios").fetchall()
            
            for user in usuarios:
                self.tree.insert("", tk.END, values=(user[0], user[1]))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando usuarios: {str(e)}")

    def _nuevo_usuario(self):
        from .nuevo_usuario_view import NuevoUsuarioView
        NuevoUsuarioView(self.controller, self)  # Pasar self como parent para modalidad

    def _editar_usuario(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para editar")
            return
        
        usuario = self.tree.item(seleccion, "values")[0]  # username
        rol = self.tree.item(seleccion, "values")[1]
        from .nuevo_usuario_view import NuevoUsuarioView
        NuevoUsuarioView(self.controller, self, usuario, rol)  # Pasar datos para edición

    def _eliminar_usuario(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
            return
        
        usuario = self.tree.item(seleccion, "values")[0]  # username
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al usuario '{usuario}'?"):
            try:
                db = DatabaseService()
                db.eliminar_usuario(usuario)
                self._cargar_usuarios()  # Actualizar lista
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar usuario: {str(e)}")

    def _on_select(self, event):
        pass  # Placeholder, puedes implementar acciones al seleccionar si es necesario

    def actualizar_lista(self):
        self._cargar_usuarios()

    def _cerrar_ventana(self):
        self.destroy()