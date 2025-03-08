from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QFont
from PyQt5.QtCore import Qt
import sys

class OdontogramaCanvas(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Dibujar imagen de fondo (opcional)
        try:
            pixmap = QPixmap("Imagenes/ImgClinica.jpeg").scaled(self.width(), self.height())
            if not pixmap.isNull():
                painter.drawPixmap(0, 0, pixmap)
        except Exception as e:
            print(f"Error al cargar la imagen: {e}")

        # Dibujar dientes (sistema básico con 32 dientes)
        pen = QPen(Qt.black, 2)
        brush = QBrush(Qt.lightGray)
        font = QFont("Arial", 10)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.setFont(font)

        # Dientes superiores (8 por lado, numeración 1-16)
        tooth_positions = [
            (200, 150), (250, 150), (300, 150), (350, 150),  # 1-4 (superior izquierda)
            (450, 150), (500, 150), (550, 150), (600, 150),  # 5-8 (superior derecha)
            (200, 200), (250, 200), (300, 200), (350, 200),  # 9-12 (superior izquierda)
            (450, 200), (500, 200), (550, 200), (600, 200)   # 13-16 (superior derecha)
        ]
        for i, (x, y) in enumerate(tooth_positions, 1):
            painter.drawEllipse(x, y, 40, 40)  # Círculo para cada diente
            painter.drawText(x + 10, y + 20, str(i))  # Numeración

        # Dientes inferiores (8 por lado, numeración 17-32)
        tooth_positions_lower = [
            (200, 350), (250, 350), (300, 350), (350, 350),  # 17-20 (inferior izquierda)
            (450, 350), (500, 350), (550, 350), (600, 350),  # 21-24 (inferior derecha)
            (200, 400), (250, 400), (300, 400), (350, 400),  # 25-28 (inferior izquierda)
            (450, 400), (500, 400), (550, 400), (600, 400)   # 29-32 (inferior derecha)
        ]
        for i, (x, y) in enumerate(tooth_positions_lower, 17):
            painter.drawEllipse(x, y, 40, 40)  # Círculo para cada diente
            painter.drawText(x + 10, y + 20, str(i))  # Numeración

class Odontograma(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Odontograma")
        self.setFixedSize(800, 600)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Canvas para el odontograma
        self.canvas = OdontogramaCanvas()
        layout.addWidget(self.canvas)

        # Añadir título en la parte superior
        self.title_label = QLabel("Odontograma", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(45)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setStyleSheet("color: #333333; background-color: rgba(255, 255, 255, 0);")
        layout.addWidget(self.title_label, alignment=Qt.AlignTop)

        # Botón para cerrar
        self.close_button = QPushButton("Cerrar", self)
        self.close_button.setStyleSheet("background-color: #F5F5F5; border: 1px solid #D3D3D3;")
        self.close_button.move(350, 500)
        self.close_button.clicked.connect(self.close)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    odontograma = Odontograma()
    odontograma.show()
    print("Odontograma iniciado. Revisa la consola para errores.")
    sys.exit(app.exec_())