import re
import tkinter as tk
from tkinter import ttk, messagebox
from models.paciente import Paciente
from datetime import datetime
from services.database_service import DatabaseService
from views.styles import configurar_estilos
class NuevoPacienteView(tk.Toplevel):
    def __init__(self, controller, paciente=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.paciente = paciente  # Paciente existente para edición, None para nuevo
        self.title("Editar Paciente" if paciente else "Nuevo Paciente")
        self.geometry("400x600")
        self.resizable(True, True)
        self._crear_formulario()
        configurar_estilos(self)  # Aplicar estilos globales
        self._centrar_ventana()
        self.lift()
        self.focus_set()
        self.grab_set()  # Ventana modal

        if paciente:
            self._cargar_datos(paciente)
    def _cargar_datos(self, paciente):
        """Carga los datos de un paciente existente en los campos"""
        self.entry_identificador.delete(0, tk.END)
        self.entry_identificador.insert(0, paciente.identificador)
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, paciente.nombre)
        self.entry_fecha_nac.delete(0, tk.END)
        self.entry_fecha_nac.insert(0, paciente.fecha_nacimiento)
        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.insert(0, paciente.telefono)
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, paciente.email)
        self.entry_direccion.delete(0, tk.END)
        self.entry_direccion.insert(0, paciente.direccion)
        self.entry_alergias.delete(0, tk.END)
        self.entry_alergias.insert(0, paciente.alergias)
        self.entry_tratamientos.delete(0, tk.END)
        self.entry_tratamientos.insert(0, paciente.tratamientos_previos)
        self.entry_notas.delete(0, tk.END)
        self.entry_notas.insert(0, paciente.notas)
        self.text_historial.delete("1.0", tk.END)
        self.text_historial.insert("1.0", paciente.historial)
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
            ("Dirección:", "entry_direccion"),
            ("Alergias:", "entry_alergias"),
            ("Tratamientos previos:", "entry_tratamientos"),
            ("Notas:", "entry_notas")
        ]

        for texto, variable in campos:
            ttk.Label(self, text=texto).pack(pady=5)
            entry = ttk.Entry(self)
            entry.pack(fill=tk.X, padx=10, pady=2)  # Añadimos pady para espaciado
            setattr(self, variable, entry)

        ttk.Label(self, text="Historial médico:").pack(pady=5)
        self.text_historial = tk.Text(self, height=5, width=40)
        self.text_historial.pack(padx=10, pady=5, fill=tk.X)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=15, fill=tk.X)  # Aseguramos que el frame use todo el ancho
        
        ttk.Button(frame_botones, text="Guardar", 
                   command=self._guardar_paciente).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(frame_botones, text="Cancelar", 
                   command=self.destroy).pack(side=tk.LEFT, padx=5, pady=5)

    def _guardar_paciente(self):
        print("Iniciando guardar paciente...")  # Depuración
        datos = {
            'identificador': self.entry_identificador.get().strip().upper(),
            'nombre': self.entry_nombre.get().strip().upper(),
            'fecha_nacimiento': self.entry_fecha_nac.get().strip(),
            'telefono': self.entry_telefono.get().strip(),
            'email': self.entry_email.get().strip(),
            'direccion': self.entry_direccion.get().strip(),
            'historial': self.text_historial.get("1.0", tk.END).strip(),
            'alergias': self.entry_alergias.get().strip(),
            'tratamientos_previos': self.entry_tratamientos.get().strip(),
            'notas': self.entry_notas.get().strip()  # Corregido: usar .get().strip() para ttk.Entry
        }

        # Validar datos básicos
        if not all([datos['identificador'], datos['nombre'], datos['fecha_nacimiento'], datos['telefono'], datos['email'], datos['direccion'], datos['historial']]):
            print("Error: Campos obligatorios vacíos")  # Depuración
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return

        # Validar formato de fecha (DD/MM/AAAA)
        try:
            datetime.strptime(datos['fecha_nacimiento'], "%d/%m/%Y")
        except ValueError:
            print("Error: Formato de fecha incorrecto")  # Depuración
            messagebox.showerror("Error", "El formato de fecha debe ser DD/MM/AAAA")
            return

        # Validar DNI o NIE
        print(f"Validando identificador: {datos['identificador']}")  # Depuración
        if not (self.validar_dni(datos['identificador']) or self.validar_nie(datos['identificador'])):
            print("Error: Identificador no válido (DNI/NIE)")  # Depuración
            messagebox.showerror("Error", "El identificador debe ser un DNI o NIE válido (ej. 12345678A o X1234567A)")
            return

        try:
            nuevo_paciente = Paciente(
                identificador=datos['identificador'],
                nombre=datos['nombre'],
                fecha_nacimiento=datos['fecha_nacimiento'],
                telefono=datos['telefono'],
                email=datos['email'],
                direccion=datos['direccion'],
                historial=datos['historial'],
                alergias=datos['alergias'],
                tratamientos_previos=datos['tratamientos_previos'],
                notas=datos['notas']
            )

            db = DatabaseService()
            print(f"Verificando si existe identificador: {datos['identificador']}")  # Depuración
            if not db.existe_identificador(datos['identificador']):
                db.guardar_paciente(nuevo_paciente)
                messagebox.showinfo("Éxito", "Paciente registrado correctamente")
                self.controller.actualizar_lista_pacientes()
                self.destroy()
            else:
                messagebox.showerror("Error", "El identificador ya está registrado")
        except ValueError as e:
            print(f"Error de ValueError en la base de datos: {str(e)}")  # Depuración
            messagebox.showerror("Error", f"Dato inválido: {str(e)}")
        except Exception as e:
            print(f"Error inesperado al guardar paciente: {str(e)}")  # Depuración
            messagebox.showerror("Error", f"Error al guardar paciente: {str(e)}")                 
    def validar_dni(self, dni):
        """Valida si un DNI es correcto (8 dígitos + 1 letra)"""
        if not re.match(r'^\d{8}[A-Z]$', dni.upper()):
            return False
        # Opcional: Verificar la letra de control
        try:
            numeros = int(dni[:-1])  # Los 8 dígitos
            letras = "TRWAGMYFPDXBNJZSQVHLCKE"
            letra_esperada = letras[numeros % 23]
            return dni[-1].upper() == letra_esperada
        except ValueError:
            return False 
    def validar_nie(self, nie):
        """Valida si un NIE es correcto (X/Y/Z + 7-8 dígitos + 1 letra)"""
        if not re.match(r'^[XYZ]\d{7,8}[A-Z]$', nie.upper()):
            return False
        # Convertir X->0, Y->1, Z->2 para calcular la letra como en DNI
        nie = nie.upper()
        prefijo = nie[0]
        if prefijo == 'X':
            numero = '0' + nie[1:-1]
        elif prefijo == 'Y':
            numero = '1' + nie[1:-1]
        elif prefijo == 'Z':
            numero = '2' + nie[1:-1]
        else:
            return False

        try:
            numeros = int(numero)
            letras = "TRWAGMYFPDXBNJZSQVHLCKE"
            letra_esperada = letras[numeros % 23]
            return nie[-1] == letra_esperada
        except ValueError:
            return False           
   