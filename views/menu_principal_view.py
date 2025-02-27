# views/menu_principal_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from views.styles import configurar_estilos
from PIL import Image, ImageTk

class MenuPrincipalView(tk.Toplevel):
    def __init__(self, controller, rol, master=None):
        super().__init__(master=master)
        self.controller = controller
        self.rol = rol
        self.title("Clínica Dental P&D")
        self.geometry("400x500")
        self._crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        configurar_estilos(self)
        self._centrar_ventana()

    def _centrar_ventana(self):
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _crear_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Clínica Dental P&D", font=("Helvetica", 16, "bold"), justify="center")
        title_label.pack(pady=(0, 20))

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True)

        # Cargar iconos (ajusta las rutas según tus archivos de iconos)
        icon_pacientes = Image.open("icons/paciente.png").resize((20, 20), Image.Resampling.LANCZOS)
        icon_usuarios = Image.open("icons/usuario.png").resize((20, 20), Image.Resampling.LANCZOS)
        icon_cerrar = Image.open("icons/cerrar.png").resize((20, 20), Image.Resampling.LANCZOS)
        icon_resumen = Image.open("icons/resumen.png").resize((20, 20), Image.Resampling.LANCZOS)  # Añade un icono para resumen

        # Convertir imágenes a PhotoImage para Tkinter
        self.photo_pacientes = ImageTk.PhotoImage(icon_pacientes)
        self.photo_usuarios = ImageTk.PhotoImage(icon_usuarios)
        self.photo_cerrar = ImageTk.PhotoImage(icon_cerrar)
        self.photo_resumen = ImageTk.PhotoImage(icon_resumen)

        # Botones simplificados
        buttons = [
            ("Gestión de Pacientes", self.controller.mostrar_pacientes, self.photo_pacientes),
            ("Resumen", self._mostrar_resumen, self.photo_resumen),  # Nuevo botón
        ]

        for i, (text, command, photo) in enumerate(buttons):
            btn = ttk.Button(buttons_frame, text=text, image=photo, compound="left", command=command, style="TButton", padding=10)
            btn.pack(fill=tk.X, pady=5)
            btn.image = photo  # Mantener referencia para evitar limpieza por el recolector de basura

        # Botón de gestión de usuarios (solo para admin)
        if self.rol == "admin":
            admin_btn = ttk.Button(buttons_frame, text="Gestión de Usuarios", image=self.photo_usuarios, compound="left", command=self.controller.mostrar_gestion_usuarios, style="TButton", padding=10)
            admin_btn.pack(fill=tk.X, pady=5)
            admin_btn.image = self.photo_usuarios

        # Botón de cerrar sesión
        logout_btn = ttk.Button(buttons_frame, text="Cerrar Sesión", image=self.photo_cerrar, compound="left", command=self.controller.cerrar_sesion, style="Logout.TButton", padding=12)
        logout_btn.pack(fill=tk.X, pady=(20, 0))
        logout_btn.image = self.photo_cerrar

    def _mostrar_resumen(self):
        """Abre la vista de resumen con estadísticas de pacientes y pagos."""
        from views.resumen_view import ResumenView  # type: ignore # Importar aquí para evitar ciclos de importación
        try:
            resumen_ventana = ResumenView(self.controller)
            resumen_ventana.protocol("WM_DELETE_WINDOW", resumen_ventana.destroy)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el resumen: {str(e)}")

    def _on_close(self):
        self.controller.cerrar_sesion()
        self.destroy()