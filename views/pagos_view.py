# views/pagos_view.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import tkinter as tk
from tkinter import ttk, messagebox
from services.database_service import DatabaseService
from models.pago import Pago
from views.styles import configurar_estilos

class PagosView(tk.Toplevel):
    def __init__(self, controller, paciente_id=None):
        super().__init__()
        self.controller = controller
        self.paciente_id = paciente_id  # Almacenar el ID si se proporciona
        self.title("Gestión de Pagos")
        self.geometry("1000x600")  # Aumentamos el tamaño para dos Treeviews
        self._crear_widgets()
        self._cargar_pacientes()  # Cargar pacientes al iniciar
        if paciente_id:
            self._cargar_pagos()  # Cargar pagos iniciales si hay un paciente_id
        configurar_estilos(self)  # Aplicar estilos globales
        self.protocol("WM_DELETE_WINDOW", self._cerrar_ventana)

    def _crear_widgets(self):
        # Frame principal para organizar los Treeviews
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para el buscador
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(search_frame, text="Buscar por ID del Paciente:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Buscar", command=self._buscar_paciente).pack(side=tk.LEFT, padx=5)

        # Treeview para mostrar pacientes
        self.tree_pacientes = ttk.Treeview(main_frame, columns=("ID", "Nombre", "Teléfono"), show="headings")
        self.tree_pacientes.heading("ID", text="Identificador")
        self.tree_pacientes.heading("Nombre", text="Nombre")
        self.tree_pacientes.heading("Teléfono", text="Teléfono")
        self.tree_pacientes.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Treeview para mostrar pagos
        self.tree_pagos = ttk.Treeview(main_frame, columns=("ID Pago", "Fecha", "Monto Total", "Monto Pagado", "Método", "Saldo"), show="headings")
        for col in ("ID Pago", "Fecha", "Monto Total", "Monto Pagado", "Método", "Saldo"):
            self.tree_pagos.heading(col, text=col)
            self.tree_pagos.column(col, width=120, anchor=tk.CENTER)  # Aumentar ancho para valores con "€"
        self.tree_pagos.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para crear nuevo pago
        btn_nuevo_pago = ttk.Button(
            self, 
            text="Nuevo Pago", 
            command=self._nuevo_pago
        )
        btn_nuevo_pago.pack(pady=10)

        # Vincular la selección en el Treeview de pacientes para actualizar pagos
        self.tree_pacientes.bind("<<TreeviewSelect>>", self._on_paciente_select)

    def _cargar_pacientes(self):
        """Obtiene y muestra todos los pacientes desde la base de datos"""
        try:
            pacientes = self.controller.db.obtener_pacientes()
            # Limpiar datos antiguos
            for item in self.tree_pacientes.get_children():
                self.tree_pacientes.delete(item)
            # Insertar nuevos datos
            for paciente in pacientes:
                self.tree_pacientes.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pacientes: {str(e)}")

    def _cargar_pagos(self):
        """Obtiene y muestra los pagos del paciente seleccionado desde la base de datos"""
        try:
            # Limpiar pagos actuales
            for item in self.tree_pagos.get_children():
                self.tree_pagos.delete(item)

            if self.paciente_id:
                pagos = self.controller.db.obtener_pagos(self.paciente_id)
                # Insertar nuevos pagos
                for pago in pagos:
                    self.tree_pagos.insert("", tk.END, values=(
                        pago.id_pago,
                        pago.fecha_pago,
                        f"€{pago.monto_total:.2f}",
                        f"€{pago.monto_pagado:.2f}",
                        pago.metodo.capitalize(),
                        f"€{pago.saldo:.2f}"
                    ))
            else:
                print("No se seleccionó un paciente, no se cargan pagos.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pagos: {str(e)}")

    def _on_paciente_select(self, event):
        """Actualiza los pagos cuando se selecciona un paciente en el Treeview"""
        seleccion = self.tree_pacientes.selection()
        if seleccion:
            self.paciente_id = self.tree_pacientes.item(seleccion, "values")[0]  # Obtener ID del paciente
            self._cargar_pagos()  # Cargar pagos del paciente seleccionado
        else:
            self.paciente_id = None
            self._cargar_pagos()  # Limpiar pagos si no hay selección

    def _buscar_paciente(self):
        """Busca un paciente por su ID y muestra solo ese paciente en el Treeview"""
        id_buscado = self.search_entry.get().strip()
        if not id_buscado:
            messagebox.showwarning("Advertencia", "Ingrese un ID de paciente para buscar")
            return

        try:
            # Obtener el paciente desde la base de datos
            paciente = self.controller.db.obtener_paciente(id_buscado)
            if paciente:
                # Limpiar el Treeview de pacientes
                for item in self.tree_pacientes.get_children():
                    self.tree_pacientes.delete(item)
                # Insertar solo el paciente encontrado
                self.tree_pacientes.insert("", tk.END, values=(
                    paciente.identificador,
                    paciente.nombre,
                    paciente.telefono
                ))
                # Actualizar el paciente_id y cargar sus pagos
                self.paciente_id = paciente.identificador
                self._cargar_pagos()
            else:
                messagebox.showerror("Error", "No se encontró un paciente con ese ID")
                # Limpiar el Treeview de pacientes
                for item in self.tree_pacientes.get_children():
                    self.tree_pacientes.delete(item)
                self.paciente_id = None
                self._cargar_pagos()
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar paciente: {str(e)}")

    def _nuevo_pago(self):
        """Abre la ventana de nuevo pago con el paciente seleccionado"""
        if not self.paciente_id:
            messagebox.showwarning("Advertencia", "Seleccione un paciente primero")
            return
        from views.nuevo_pago_view import NuevoPagoView
        NuevoPagoView(self.controller, self.paciente_id)
        self._cargar_pagos()  # Actualizar lista de pagos después de crear

    def _cerrar_ventana(self):
        if 'pagos' in self.controller._ventanas_abiertas:
            del self.controller._ventanas_abiertas['pagos']
        self.destroy()