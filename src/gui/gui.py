from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout,
    QPushButton, QLabel, QVBoxLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
import sys


class Board(QWidget):

    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        # Encabezados
        for col in range(10):
            label = QLabel(str(col + 1))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, 0, col + 1)

        # Filas
        for row in range(10):
            label = QLabel(chr(ord('A') + row))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label, row + 1, 0)

        # Casillas
        for row in range(10):
            for col in range(10):
                cell = QPushButton()
                cell.setFixedSize(40, 40)

                # Solo apariencia; no hacemos nada con el botón
                layout.addWidget(cell, row + 1, col + 1)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Battleship")

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        title = QLabel("BATTLESHIP")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        boards_layout = QHBoxLayout()

        own_layout = QVBoxLayout()
        own_layout.addWidget(QLabel("TABLERO PROPIO"))
        own_layout.addWidget(Board())

        enemy_layout = QVBoxLayout()
        enemy_layout.addWidget(QLabel("TABLERO ENEMIGO"))
        enemy_layout.addWidget(Board())

        boards_layout.addLayout(own_layout)
        boards_layout.addLayout(enemy_layout)

        main_layout.addLayout(boards_layout)

        buttons = QHBoxLayout()

        restart = QPushButton("Reiniciar")
        exit_button = QPushButton("Salir")

        buttons.addWidget(restart)
        buttons.addWidget(exit_button)

        main_layout.addLayout(buttons)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())