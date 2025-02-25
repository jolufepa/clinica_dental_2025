import tkinter as tk
from tkinter import ttk

def configurar_estilos(root=None):
    """
    Configura los estilos globales para las vistas de la aplicación.
    root: Widget raíz (opcional, para aplicar estilos directamente si es necesario)
    """
    estilo = ttk.Style()
    estilo.theme_use('clam')  # O 'alt', 'default', según prefieras

    # Estilos para botones
    estilo.configure('TButton', foreground='white', background='#4CAF50', font=('Arial', 10, 'bold'), padding=6)
    estilo.map('TButton', background=[('active', '#45a049')])

    # Estilos para entradas
    estilo.configure('TEntry', fieldbackground='white', font=('Arial', 10), padding=5)
    estilo.map('TEntry', fieldbackground=[('focus', '#e0e0e0')])

    # Estilos para Combobox
    estilo.configure('TCombobox', fieldbackground='white', font=('Arial', 10), padding=5)
    estilo.map('TCombobox', fieldbackground=[('focus', '#e0e0e0')])

    # Estilos para Treeview
    estilo.configure('Treeview', background='white', fieldbackground='white', font=('Arial', 10))
    estilo.configure('Treeview.Heading', background='#4CAF50', foreground='white', font=('Arial', 10, 'bold'))

    # Estilos para etiquetas
    estilo.configure('TLabel', font=('Arial', 10), background='#f0f0f0')

    # Si se pasa un root, aplica los estilos directamente
    if root:
        root.style = estilo