import sys
import random
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

# Importaciones de tu proyecto
from gui.gui import MainWindow
from gamelogic.board import Board, Ship
from gamelogic.player import Player
from gamelogic.game import Game
from agents.agent import SimpleReflexAgent, GoalBasedAgent, OptimalPDFAgent

class GameController:
    def __init__(self, window: MainWindow):
        self.window = window
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_turn)
        
        # Conectar los botones de la GUI
        self.window.btn_normal.clicked.connect(self.start_normal_match)
        self.window.btn_simular.clicked.connect(self.run_simulation)
        self.window.restart_button.clicked.connect(self.stop_and_reset)

    def stop_and_reset(self):
        """Detiene cualquier partida en curso y limpia los tableros."""
        self.timer.stop()
        self.window.restart_game()
        self.window.update_status("Partida detenida. Elige un modo para comenzar.")

    def _get_agent_instance(self, agent_name: str):
        """Devuelve una nueva instancia del agente seleccionado en el ComboBox."""
        if agent_name == "IA Reactiva":
            return SimpleReflexAgent()
        elif agent_name == "IA por Objetivos":
            return GoalBasedAgent()
        else:
            return OptimalPDFAgent()

    def _get_random_fleet(self):
        """Genera una flota aleatoria para dar variabilidad a la IA en las simulaciones."""
        flotas = [
            (Ship(5, 1, (0, 0)), Ship(4, 1, (2, 2)), Ship(3, 1, (4, 4)), Ship(3, 1, (6, 6)), Ship(2, 1, (8, 8))),
            (Ship(1, 5, (0, 0)), Ship(1, 4, (2, 2)), Ship(1, 3, (4, 4)), Ship(1, 3, (6, 6)), Ship(1, 2, (8, 8))),
            (Ship(5, 1, (9, 0)), Ship(4, 1, (7, 2)), Ship(3, 1, (5, 4)), Ship(3, 1, (3, 6)), Ship(2, 1, (1, 8))),
            (Ship(1, 5, (0, 9)), Ship(1, 4, (2, 7)), Ship(1, 3, (4, 5)), Ship(1, 3, (6, 3)), Ship(1, 2, (8, 1))),
            (Ship(5, 1, (0, 5)), Ship(4, 1, (2, 6)), Ship(3, 1, (4, 7)), Ship(3, 1, (6, 0)), Ship(2, 1, (8, 1)))
        ]
        return random.choice(flotas)

    def setup_match(self):
        """Prepara los tableros y jugadores leyendo la configuración de la UI."""
        board_a = Board(self._get_random_fleet())
        board_b = Board(self._get_random_fleet())
        
        agent_a = self._get_agent_instance(self.window.combo_a.currentText())
        agent_b = self._get_agent_instance(self.window.combo_b.currentText())
        
        self.player_a = Player(agent_a, board_a)
        self.player_b = Player(agent_b, board_b)
        self.game = Game(self.player_a, self.player_b)

    def start_normal_match(self):
        """Inicia el modo visual."""
        self.timer.stop()
        self.setup_match()
        self.window.restart_game()
        self.render_boards()
        self.window.update_status("Modo Visual: Partida en curso...")
        self.timer.start(500) # 500ms por turno

    def play_turn(self):
        """Lógica para ejecutar un solo turno en la interfaz gráfica."""
        game_continues = self.game.take_next_move()
        self.render_boards()
        
        if not game_continues:
            self.timer.stop()
            modelo_ganador = self.window.combo_a.currentText() if self.game.current_player == self.player_a else self.window.combo_b.currentText()
            ganador = f"Player A ({modelo_ganador})" if self.game.current_player == self.player_a else f"Player B ({modelo_ganador})"
            self.window.update_status(f"¡Terminado! Ganó {ganador}")
            self.window.show_winner(ganador)

    def run_simulation(self):
        """Simula 100 partidas sin gráficos para análisis estadístico."""
        self.timer.stop()
        self.window.update_status("Simulando 100 partidas... por favor espera.")
        QApplication.processEvents()
        
        wins_a = 0
        wins_b = 0
        total_games = 100

        for _ in range(total_games):
            self.setup_match()
            while self.game.take_next_move():
                pass 
            
            if self.game.current_player == self.player_a:
                wins_a += 1
            else:
                wins_b += 1

        modelo_a = self.window.combo_a.currentText()
        modelo_b = self.window.combo_b.currentText()
        
        resultado_txt = (f"Resultados de {total_games} simulaciones:\n"
                         f"Player A ({modelo_a}): {wins_a} victorias\n"
                         f"Player B ({modelo_b}): {wins_b} victorias")
        
        self.window.update_status("Simulación finalizada.")
        QMessageBox.information(self.window, "Análisis Estadístico", resultado_txt)

    def render_boards(self):
        """Lee las matrices en memoria y las traduce a la interfaz gráfica."""
        for x in range(10):
            for y in range(10):
                estado_a = self.player_a.get_matrix_board()[x][y]
                if estado_a == 'X': self.window.own_board.mark_miss(x, y)
                elif estado_a == 'O': self.window.own_board.mark_hit(x, y)
                elif estado_a == 'H': self.window.own_board.mark_sunk(x, y)

                estado_b = self.player_b.get_matrix_board()[x][y]
                if estado_b == 'X': self.window.enemy_board.mark_miss(x, y)
                elif estado_b == 'O': self.window.enemy_board.mark_hit(x, y)
                elif estado_b == 'H': self.window.enemy_board.mark_sunk(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    controller = GameController(window)
    window.show()
    sys.exit(app.exec())