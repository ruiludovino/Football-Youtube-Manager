# edit_window.py
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class EditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alterar / Editar Clip")
        self.setGeometry(400, 200, 600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        label = QLabel("Janela de Edição de Clip\n(Em desenvolvimento – aqui vais poder editar clipes existentes)")
        label.setStyleSheet("font-size: 16px; color: #34495e;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)