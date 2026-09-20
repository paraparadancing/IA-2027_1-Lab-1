import sys
import random
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer

# Importaciones de tu proyecto
from gui.gui import MainWindow
from gamelogic.board import Board, Ship, HitResult
from gamelogic.player import Player
from gamelogic.game import Game
from agents.agent import SimpleReflexAgent, GoalBasedAgent, OptimalPDFAgent

class GameController:
    def __init__(self, window: MainWindow):
        self.window = window
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_turn)

        # Variables para el modo humano
        self.human_board = None
        self.ai_player = None
        self.human_fleet = None
        self.human_attacks = set()
        self.human_game_active = False
        self.ai_turn_pending = False
        
        # Conectar los botones de la GUI
        self.window.btn_normal.clicked.connect(self.start_normal_match)
        self.window.btn_humano.clicked.connect(self.start_human_match)
        self.window.btn_simular.clicked.connect(self.run_simulation)
        self.window.restart_button.clicked.connect(self.stop_and_reset)

        # Detectar cuando el jugador humano presiona una casilla.
        self.window.enemy_board.cell_clicked.connect(
            self.human_cell_clicked
        )

    def stop_and_reset(self):
        """Detiene cualquier partida en curso y limpia los tableros."""
        self.timer.stop()

        self.human_game_active = False
        self.ai_turn_pending = False
        self.human_board = None
        self.ai_player = None
        self.human_fleet = None
        self.human_attacks = set()

        self.window.enemy_board.set_enabled(False)

        self.window.restart_game()
        self.window.update_status("Partida detenida. Elige un modo para comenzar.")

    def _get_agent_instance(self, agent_name: str):
        if agent_name == "Simple reflex agent":
            return SimpleReflexAgent()
        elif agent_name == "Goal-based agent":
            return GoalBasedAgent()
        elif agent_name == "Optimal performance agent":
            return OptimalPDFAgent()
        else:
            raise ValueError(f"Agente no reconocido: {agent_name}")

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

        self.human_game_active = False
        self.ai_turn_pending = False
        self.window.enemy_board.set_enabled(False)

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
        self.human_game_active = False
        self.ai_turn_pending = False
        self.window.enemy_board.set_enabled(False)

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

    # ========================================================
    # MODO HUMANO CONTRA IA
    # ========================================================
    def start_human_match(self):
        """Inicia una partida donde el usuario juega contra la IA."""
        self.timer.stop()

        # Activar el modo humano.
        self.human_game_active = True
        self.ai_turn_pending = False
        self.human_attacks = set()

        # Crear el tablero y la flota del jugador humano.
        self.human_fleet = self._get_random_fleet()
        self.human_board = Board(self.human_fleet)

        # Crear el tablero de la IA.
        ai_board = Board(self._get_random_fleet())

        # Player B será la IA seleccionada en la interfaz.
        ai_agent = self._get_agent_instance(
            self.window.combo_b.currentText()
        )

        self.ai_player = Player(
            ai_agent,
            ai_board
        )

        # Reiniciar la interfaz.
        self.window.restart_game()

        # Mostrar los barcos del jugador humano.
        self.render_human_board()

        # El tablero enemigo empieza habilitado porque
        # el jugador humano tiene el primer turno.
        self.window.enemy_board.set_enabled(True)

        self.window.update_status(
            f"Modo Humano: Tú juegas contra "
            f"{self.window.combo_b.currentText()}. "
            f"Selecciona una casilla enemiga."
        )

    def human_cell_clicked(self, row, col):
        """Procesa el disparo realizado por el jugador humano."""

        # Si no estamos en una partida humana, ignorar el clic.
        if not self.human_game_active:
            return

        # Evitar que el jugador dispare mientras la IA está jugando.
        if self.ai_turn_pending:
            return

        coordinates = (row, col)

        # Evitar disparar dos veces sobre la misma casilla.
        if coordinates in self.human_attacks:
            self.window.update_status(
                "Esa casilla ya fue atacada. Selecciona otra."
            )
            return

        # Registrar el disparo.
        self.human_attacks.add(coordinates)

        # Realizar el ataque sobre el tablero de la IA.
        attack_result = self.ai_player.take_move(coordinates)

        # Actualizar visualmente el tablero enemigo.
        self.render_human_enemy_board()

        # Si todos los barcos de la IA fueron destruidos,
        # el jugador humano gana.
        if attack_result == HitResult.DEFEAT:
            self.human_game_active = False
            self.ai_turn_pending = False
            self.window.enemy_board.set_enabled(False)

            self.window.update_status(
                "¡Terminaste con toda la flota enemiga!"
            )

            self.window.show_winner("Tú")
            return

        # El turno pasa a la IA.
        self.ai_turn_pending = True
        self.window.enemy_board.set_enabled(False)

        if attack_result == HitResult.HIT:
            self.window.update_status(
                f"¡Impacto en {chr(ord('A') + row)}{col + 1}! "
                f"La IA está preparando su turno..."
            )
        else:
            self.window.update_status(
                f"Agua en {chr(ord('A') + row)}{col + 1}. "
                f"La IA está preparando su turno..."
            )

        # Esperar medio segundo antes de que responda la IA.
        QTimer.singleShot(
            500,
            self.ai_make_move
        )

    def ai_make_move(self):
        """Realiza el turno de la IA contra el jugador humano."""

        # Comprobar que la partida siga activa.
        if not self.human_game_active:
            return

        # La IA analiza el tablero del jugador humano.
        attack_coordinates = self.ai_player.make_move(
            self.human_board.get_matrix_board()
        )

        row, col = attack_coordinates

        # La IA realiza su ataque.
        attack_result = self.human_board.take_move(
            attack_coordinates
        )

        # Actualizar visualmente el tablero humano.
        self.render_human_board()

        # Si la IA destruyó todos los barcos humanos,
        # la IA gana.
        if attack_result == HitResult.DEFEAT:
            self.human_game_active = False
            self.ai_turn_pending = False
            self.window.enemy_board.set_enabled(False)

            self.window.update_status(
                "La IA destruyó toda tu flota."
            )

            self.window.show_winner(
                f"IA ({self.window.combo_b.currentText()})"
            )
            return

        # Regresar el turno al jugador humano.
        self.ai_turn_pending = False
        self.window.enemy_board.set_enabled(True)

        coordenada_texto = f"{chr(ord('A') + row)}{col + 1}"

        if attack_result == HitResult.HIT:
            self.window.update_status(
                f"La IA atacó {coordenada_texto}: "
                f"¡impacto! Es tu turno."
            )
        else:
            self.window.update_status(
                f"La IA atacó {coordenada_texto}: "
                f"agua. Es tu turno."
            )

    def render_human_board(self):
        """Muestra el tablero y los barcos del jugador humano."""

        # Mostrar primero todos los barcos humanos.
        for ship in self.human_fleet:
            for row, col in ship.get_boxes():
                self.window.own_board.show_ship(
                    row,
                    col
                )

        # Mostrar los ataques que ya recibió el jugador.
        board_matrix = self.human_board.get_matrix_board()

        for x in range(10):
            for y in range(10):
                estado = board_matrix[x][y]

                if estado == 'X':
                    self.window.own_board.mark_miss(
                        x,
                        y
                    )
                elif estado == 'O':
                    self.window.own_board.mark_hit(
                        x,
                        y
                    )
                elif estado == 'H':
                    self.window.own_board.mark_sunk(
                        x,
                        y
                    )

    def render_human_enemy_board(self):
        """Muestra solamente los resultados de los ataques humanos."""

        board_matrix = self.ai_player.get_matrix_board()

        for x in range(10):
            for y in range(10):
                estado = board_matrix[x][y]

                if estado == 'X':
                    self.window.enemy_board.mark_miss(
                        x,
                        y
                    )
                elif estado == 'O':
                    self.window.enemy_board.mark_hit(
                        x,
                        y
                    )
                elif estado == 'H':
                    self.window.enemy_board.mark_sunk(
                        x,
                        y
                    )

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