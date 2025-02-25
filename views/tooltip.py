import tkinter as tk

class ToolTip:
    def __init__(self, widget, text):
        """
        Crea un tooltip para un widget de Tkinter que muestra el texto al pasar el ratón.
        
        Args:
            widget: El widget de Tkinter (por ejemplo, ttk.Button) al que se añadirá el tooltip.
            text: El texto que se mostrará en el tooltip.
        """
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Muestra el tooltip cuando el ratón entra en el widget."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)  # Quita el borde del tooltip
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="yellow", relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack(padx=2, pady=2)

    def hide_tooltip(self, event=None):
        """Oculta el tooltip cuando el ratón sale del widget."""
        if self.tooltip:
            self.tooltip.destroy()