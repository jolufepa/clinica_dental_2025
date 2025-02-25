# views/nuevo_usuario_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from views.styles import configurar_estilos
class NuevoUsuarioView(tk.Toplevel):
    def __init__(self, controller, parent=None, username=None, role=None):
        super().__init__(parent)
        self.controller = controller
        self.parent = parent  # Guardar la referencia a GestionUsuariosView
        self.username = username  # Para edición, si existe
        self.title("Nuevo Usuario" if not username else "Editar Usuario")
        self.geometry("400x300")
        self._crear_formulario()
        configurar_estilos(self)  # Aplicar estilos globales
        self._centrar_ventana()
        self.lift()
        self.focus_set()
        self.grab_set()  # Modal

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'+{x}+{y}')

    def _crear_formulario(self):
        ttk.Label(self, text="Usuario:").pack(pady=5)
        self.entry_username = ttk.Entry(self)
        self.entry_username.pack(fill=tk.X, padx=10)

        ttk.Label(self, text="Contraseña:").pack(pady=5)
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.pack(fill=tk.X, padx=10)
        ttk.Label(self, text="Confirmar Contraseña:").pack(pady=5)
        self.entry_confirm_password = ttk.Entry(self, show="*")
        self.entry_confirm_password.pack(fill=tk.X, padx=10)
        ttk.Label(self, text="Rol:").pack(pady=5)
        self.combo_rol = ttk.Combobox(self, values=["admin", "recepción"])
        self.combo_rol.pack(fill=tk.X, padx=10)
        self.combo_rol.set("recepción")  # Valor por defecto

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15)
        ttk.Button(frame_botones, text="Guardar", command=self._guardar_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Cancelar", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _cargar_datos(self, username, role):
        self.entry_username.insert(0, username)
        self.entry_username.config(state='disabled')  # Username no editable en edición
        self.combo_rol.set(role)
        self.entry_password.delete(0, tk.END)
        self.entry_password.insert(0, "********")  # Indicar que hay una contraseña existente

    def _guardar_usuario(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        role = self.combo_rol.get().strip()
        confirm_password = self.entry_confirm_password.get().strip()
        if password != confirm_password and password and confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden")
            return
        print(f"Guardando usuario {username}, contraseña: '{password}', rol: {role}")  # Depuración

        if not all([username, role]):
            messagebox.showerror("Error", "Usuario y rol son obligatorios")
            return

        if role not in ["admin", "recepción"]:
            messagebox.showerror("Error", "El rol debe ser 'admin' o 'recepción'")
            return

        try:
            db = DatabaseService()
            if self.username:  # Edición
                # Verificar si se cambió la contraseña
                if not password or password == "********":
                    # No cambiar la contraseña, solo actualizar el rol si es necesario
                    current_user = db.cursor.execute("SELECT password, role FROM usuarios WHERE username = ?", (username,)).fetchone()
                    if current_user:
                        current_password, current_role = current_user
                        if current_role != role:
                            db.actualizar_usuario(username, None, role)  # No cambiar contraseña
                            messagebox.showinfo("Éxito", "Rol del usuario actualizado correctamente")
                        else:
                            messagebox.showinfo("Éxito", "No se realizaron cambios")
                    else:
                        messagebox.showerror("Error", "Usuario no encontrado")
                else:
                    # Cambiar contraseña solo si se ingresó una nueva
                    print(f"Intentando cambiar contraseña para {username}, nueva contraseña: '{password}'")  # Depuración
                    # Verificar si es un usuario crítico (como "admin1")
                    if username.lower() == "admin1" and not messagebox.askyesno("Confirmar", f"¿Está seguro de cambiar la contraseña de '{username}'? Esto podría bloquear el acceso si la nueva contraseña es incorrecta."):
                        return
                    # Validar que la contraseña sea una cadena válida
                    if not password or not isinstance(password, str):
                        messagebox.showerror("Error", "Debe ingresar una contraseña válida para cambiarla")
                        return
                    db.actualizar_usuario(username, password, role)
                    messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                    # Verificar el hash almacenado después de guardar
                    stored_hash = db.cursor.execute("SELECT password FROM usuarios WHERE username = ?", (username,)).fetchone()[0]
                    print(f"Hash almacenado en la base de datos después de guardar: {stored_hash}")
            else:  # Nuevo usuario
                if not password:
                    messagebox.showerror("Error", "La contraseña es obligatoria para nuevos usuarios")
                    return
                if db.verificar_usuario(username, password):
                    messagebox.showerror("Error", "El usuario ya existe")
                    return
                db.crear_usuario(username, password, role)
                messagebox.showinfo("Éxito", "Usuario creado correctamente")

            if self.parent:  # Actualizar lista en GestionUsuariosView
                self.parent.actualizar_lista()
            self.destroy()
        except ValueError as e:
            print(f"Error de validación: {str(e)}")  # Depuración
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            print(f"Error al guardar usuario: {str(e)}")  # Depuración
            messagebox.showerror("Error", f"Error al guardar usuario: {str(e)}")

    def destroy(self):
        super().destroy()