from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout,
    QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QMessageBox, QComboBox, QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal
import sys

# PySide6 se encarga de la interfaz grafica.
# sys se utiliza para iniciar/cerrar correctamente la aplicacion.


# ============================================================
# TABLERO VISUAL
# ============================================================
class BoardWidget(QWidget):

    # Esta señal avisa qué casilla fue presionada.
    # Envía fila y columna.
    cell_clicked = Signal(int, int)

    def __init__(self, interactive=False):
        super().__init__()

        # Indica si se pueden presionar las casillas.
        self.interactive = interactive

        # Aquí guardamos los 100 botones del tablero.
        # Ejemplo:
        # self.cells[0][0] = A1
        # self.cells[1][0] = B1
        self.cells = []

        layout = QGridLayout()
        self.setLayout(layout)

        # ----------------------------------------------------
        # Encabezados de columnas: 1 - 10
        # ----------------------------------------------------
        for col in range(10):
            label = QLabel(str(col + 1))
            label.setAlignment(Qt.AlignCenter)

            layout.addWidget(
                label,
                0,
                col + 1
            )

        # ----------------------------------------------------
        # Encabezados de filas: A - J
        # ----------------------------------------------------
        for row in range(10):
            label = QLabel(chr(ord("A") + row))
            label.setAlignment(Qt.AlignCenter)

            layout.addWidget(
                label,
                row + 1,
                0
            )

        # ----------------------------------------------------
        # Crear las 100 casillas
        # ----------------------------------------------------
        for row in range(10):

            row_cells = []

            for col in range(10):

                cell = QPushButton()

                cell.setFixedSize(40, 40)

                # Guardamos la coordenada dentro del botón.
                cell.setProperty("row", row)
                cell.setProperty("col", col)

                # Cuando presionamos el botón mandamos
                # su fila y columna.
                cell.clicked.connect(
                    lambda checked=False, r=row, c=col:
                    self.on_cell_clicked(r, c)
                )

                # Permitir o bloquear clics.
                cell.setEnabled(self.interactive)

                layout.addWidget(
                    cell,
                    row + 1,
                    col + 1
                )

                # Guardamos el botón.
                row_cells.append(cell)

            # Guardamos toda la fila.
            self.cells.append(row_cells)

    # ========================================================
    # CUANDO SE PRESIONA UNA CASILLA
    # ========================================================
    def on_cell_clicked(self, row, col):

        self.cell_clicked.emit(row, col)

    # ========================================================
    # MOSTRAR UN BARCO
    # ========================================================
    def show_ship(self, row, col):

        cell = self.cells[row][col]

        cell.setText("■")

        cell.setStyleSheet(
            "background-color: gray;"
        )

    # ========================================================
    # MOSTRAR IMPACTO
    # ========================================================
    def mark_hit(self, row, col):

        cell = self.cells[row][col]

        cell.setText("X")

        cell.setStyleSheet(
            "background-color: red;"
            "color: white;"
            "font-weight: bold;"
        )

    # ========================================================
    # MOSTRAR DISPARO FALLIDO
    # ========================================================
    def mark_miss(self, row, col):

        cell = self.cells[row][col]

        cell.setText("•")

        cell.setStyleSheet(
            "background-color: lightblue;"
        )

    # ========================================================
    # MOSTRAR BARCO HUNDIDO
    # ========================================================
    def mark_sunk(self, row, col):

        cell = self.cells[row][col]

        cell.setText("X")

        cell.setStyleSheet(
            "background-color: darkred;"
            "color: white;"
            "font-weight: bold;"
        )

    # ========================================================
    # LIMPIAR TABLERO
    # ========================================================
    def reset_board(self):

        for row in range(10):

            for col in range(10):

                cell = self.cells[row][col]

                cell.setText("")
                cell.setStyleSheet("")

                # Regresa al estado inicial.
                cell.setEnabled(self.interactive)

    # ========================================================
    # ACTIVAR O DESACTIVAR TABLERO
    # ========================================================
    def set_enabled(self, enabled):

        for row in range(10):

            for col in range(10):

                self.cells[row][col].setEnabled(enabled)


# ============================================================
# VENTANA PRINCIPAL
# ============================================================
class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Battleship - AI")

        main_layout = QVBoxLayout()

        self.setLayout(main_layout)

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------
        title = QLabel("BATTLESHIP")

        title.setAlignment(Qt.AlignCenter)

        main_layout.addWidget(title)

        # ----------------------------------------------------
        # PANEL DE CONTROL DE INTELIGENCIA ARTIFICIAL
        # ----------------------------------------------------
        control_group = QGroupBox("AI Laboratory Options")
        control_layout = QHBoxLayout()

        # IA Player A
        form_a = QFormLayout()
        self.combo_a = QComboBox()
        self.combo_a.addItems(["Simple reflex agent", "Goal-based agent", "Optimal performance agent"])
        self.combo_a.setCurrentIndex(1)
        form_a.addRow("Player A Model:", self.combo_a)
        
        # IA Player B
        form_b = QFormLayout()
        self.combo_b = QComboBox()
        self.combo_b.addItems(["Simple reflex agent", "Goal-based agent", "Optimal performance agent"])
        self.combo_b.setCurrentIndex(2)
        form_b.addRow("Player B Model:", self.combo_b)

        control_layout.addLayout(form_a)
        control_layout.addLayout(form_b)
        control_group.setLayout(control_layout)
        
        main_layout.addWidget(control_group)

        # ----------------------------------------------------
        # BOTONES DE SIMULACIÓN
        # ----------------------------------------------------
        sim_buttons_layout = QHBoxLayout()
        
        self.btn_normal = QPushButton("▶ Start Visual Match")
        self.btn_simular = QPushButton("⚡ Simulate 100 Matches")
        
        sim_buttons_layout.addWidget(self.btn_normal)
        sim_buttons_layout.addWidget(self.btn_simular)
        
        main_layout.addLayout(sim_buttons_layout)

        # ----------------------------------------------------
        # MENSAJE DE ESTADO
        # ----------------------------------------------------
        self.status_label = QLabel(
            "Game ready. Choose a mode."
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        main_layout.addWidget(
            self.status_label
        )

        # ----------------------------------------------------
        # ETIQUETA DE ESTADÍSTICAS
        # ----------------------------------------------------
        self.lbl_stats = QLabel("")
        self.lbl_stats.setAlignment(Qt.AlignCenter)
        self.lbl_stats.setStyleSheet("font-weight: bold; color: green;")
        
        main_layout.addWidget(
            self.lbl_stats
        )

        # ----------------------------------------------------
        # CONTENEDOR DE LOS DOS TABLEROS
        # ----------------------------------------------------
        boards_layout = QHBoxLayout()

        # ==============================
        # TABLERO PROPIO (Player A)
        # ==============================
        own_layout = QVBoxLayout()

        own_title = QLabel(
            "OWN BOARD (Player A)"
        )

        own_title.setAlignment(
            Qt.AlignCenter
        )

        own_layout.addWidget(
            own_title
        )

        # Guardamos el tablero.
        self.own_board = BoardWidget(
            interactive=False
        )

        own_layout.addWidget(
            self.own_board
        )

        # ==============================
        # TABLERO ENEMIGO (Player B)
        # ==============================
        enemy_layout = QVBoxLayout()

        enemy_title = QLabel(
            "ENEMY BOARD (Player B)"
        )

        enemy_title.setAlignment(
            Qt.AlignCenter
        )

        enemy_layout.addWidget(
            enemy_title
        )

        self.enemy_board = BoardWidget(
            interactive=False
        )

        enemy_layout.addWidget(
            self.enemy_board
        )

        # Agregamos ambos tableros.
        boards_layout.addLayout(
            own_layout
        )

        boards_layout.addLayout(
            enemy_layout
        )

        main_layout.addLayout(
            boards_layout
        )

        # ----------------------------------------------------
        # BOTONES ORIGINALES
        # ----------------------------------------------------
        buttons = QHBoxLayout()

        self.restart_button = QPushButton(
            "Stop / Restart"
        )

        self.exit_button = QPushButton(
            "Exit"
        )

        buttons.addWidget(
            self.restart_button
        )

        buttons.addWidget(
            self.exit_button
        )

        main_layout.addLayout(
            buttons
        )

        # ----------------------------------------------------
        # CONECTAR BOTONES
        # ----------------------------------------------------

        # (La lógica de conectar los nuevos botones se hace en main.py)

        # Cerrar programa.
        self.exit_button.clicked.connect(
            self.close
        )

        # Detectar clic en tablero enemigo (por si juegas contra IA luego).
        self.enemy_board.cell_clicked.connect(
            self.enemy_cell_clicked
        )

    # ========================================================
    # CUANDO SE PRESIONA TABLERO ENEMIGO
    # ========================================================
    def enemy_cell_clicked(self, row, col):

        # Convertimos:
        # row 0 -> A
        # row 1 -> B
        # etc.
        letter = chr(
            ord("A") + row
        )

        # col empieza en 0,
        # pero visualmente empieza en 1.
        number = col + 1

        self.status_label.setText(
            f"Selected cell: "
            f"{letter}{number}"
        )

        # IMPORTANTE:
        # Aquí NO decidimos si fue agua o impacto.
        #
        # Eso después vendrá desde gamelogic.

    # ========================================================
    # REINICIAR INTERFAZ
    # ========================================================
    def restart_game(self):

        self.own_board.reset_board()

        self.enemy_board.reset_board()

        self.status_label.setText(
            "Game restarted"
        )

        # Borrar también las estadísticas.
        self.lbl_stats.setText("")

    # ========================================================
    # CAMBIAR TEXTO DE ESTADO
    # ========================================================
    def update_status(self, message):

        self.status_label.setText(
            message
        )

    # ========================================================
    # MOSTRAR GANADOR
    # ========================================================
    def show_winner(self, winner):

        QMessageBox.information(
            self,
            "Game Over",
            f"Winner: {winner}"
        )

        # Bloquear tableros al terminar.
        self.own_board.set_enabled(False)

        self.enemy_board.set_enabled(False)


# ============================================================
# EJECUTAR APLICACIÓN
# ============================================================
if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec())