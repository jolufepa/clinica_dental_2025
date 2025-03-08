# views/styles.py
import tkinter as tk
from tkinter import ttk

def configurar_estilos(root):
    if not isinstance(root, (tk.Tk, tk.Toplevel)):
        raise ValueError("El argumento 'root' debe ser una instancia de tk.Tk o tk.Toplevel")
    
    style = ttk.Style(root)
    
    # Fondo de la ventana
    root.configure(bg="#f0f0f0")  # Mantener gris claro original
    
    # Estilo para los botones principales (verde con texto negro)
    style.configure("TButton", 
                    background="#4CAF50",  # Verde suave
                    foreground="black",    # Texto negro para legibilidad
                    font=("Helvetica", 10, "bold"),
                    padding=10,
                    relief="flat")         # Bordes planos
    style.map("TButton",
              background=[("active", "#45a049")])  # Cambio de color al pasar el ratón
    
    # Estilo para el botón de cerrar sesión (rojo claro)
    style.configure("Logout.TButton", 
                    background="#E57373",  # Rojo más claro
                    foreground="black",    # Texto negro
                    font=("Helvetica", 10, "bold"),
                    padding=12,
                    relief="flat")
    style.map("Logout.TButton",
              background=[("active", "#D32F2F")])  
    
    # Estilo para etiquetas (título)
    style.configure("TLabel", 
                    font=("Helvetica", 16, "bold"),  # Tamaño original con ajuste
                    foreground="#333333")  # Gris oscuro
    
    root.option_add("*TButton*Compound", "left")  # Para iconos