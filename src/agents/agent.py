import random
from abc import ABC, abstractmethod

class Agent(ABC):
    @abstractmethod
    def make_move(self, input_matrix_board: list[list[str]]) -> tuple[int, int]:
        pass

# ==========================================
# 1. AGENTE REACTIVO SIMPLE
# ==========================================
class SimpleReflexAgent(Agent):
    def __init__(self, cols=10, rows=10):
        self.cols = cols
        self.rows = rows

    def make_move(self, input_matrix_board: list[list[str]]) -> tuple[int, int]:
        for x in range(self.cols):
            for y in range(self.rows):
                if input_matrix_board[x][y] == 'O':
                    vecinos = self._get_valid_neighbors(x, y, input_matrix_board)
                    if vecinos:
                        return random.choice(vecinos)
        return self._random_shot(input_matrix_board)

    def _get_valid_neighbors(self, x, y, board):
        validos = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows:
                if board[nx][ny] is None:
                    validos.append((nx, ny))
        return validos

    def _random_shot(self, board):
        opciones = [(x, y) for x in range(self.cols) for y in range(self.rows) if board[x][y] is None]
        return random.choice(opciones) if opciones else (0,0)

# ==========================================
# 2. AGENTE BASADO EN OBJETIVOS
# ==========================================
class GoalBasedAgent(Agent):
    def __init__(self, cols=10, rows=10):
        self.cols = cols
        self.rows = rows

    def make_move(self, input_matrix_board: list[list[str]]) -> tuple[int, int]:
        impactos_activos = []
        for x in range(self.cols):
            for y in range(self.rows):
                if input_matrix_board[x][y] == 'O':
                    impactos_activos.append((x, y))

        if impactos_activos:
            if len(impactos_activos) > 1:
                return self._continue_line(impactos_activos, input_matrix_board)
            else:
                x, y = impactos_activos[0]
                return self._get_valid_neighbor(x, y, input_matrix_board)
        
        return self._checkerboard_shot(input_matrix_board)

    def _continue_line(self, hits, board):
        p1, p2 = hits[0], hits[1]
        es_horizontal = (p1[1] == p2[1])

        for x, y in hits:
            direcciones = [(-1, 0), (1, 0)] if es_horizontal else [(0, -1), (0, 1)]
            for dx, dy in direcciones:
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows and board[nx][ny] is None:
                    return (nx, ny)
        return self._get_valid_neighbor(hits[0][0], hits[0][1], board)

    def _get_valid_neighbor(self, x, y, board):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows and board[nx][ny] is None:
                return (nx, ny)
        return self._checkerboard_shot(board)

    def _checkerboard_shot(self, board):
        opciones = [(x, y) for x in range(self.cols) for y in range(self.rows) 
                    if board[x][y] is None and (x + y) % 2 == 0]
        if not opciones:
            opciones = [(x, y) for x in range(self.cols) for y in range(self.rows) if board[x][y] is None]
        return random.choice(opciones) if opciones else (0,0)

# ==========================================
# 3. AGENTE ÓPTIMO (PDF)
# ==========================================
class OptimalPDFAgent(Agent):
    def __init__(self, cols=10, rows=10):
        self.cols = cols
        self.rows = rows
        self.barcos_restantes = [5, 4, 3, 3, 2]

    def make_move(self, input_matrix_board: list[list[str]]) -> tuple[int, int]:
        heatmap = [[0 for _ in range(self.rows)] for _ in range(self.cols)]
        
        for longitud in self.barcos_restantes:
            for x in range(self.cols - longitud + 1):
                for y in range(self.rows):
                    self._evaluate_position(input_matrix_board, heatmap, x, y, longitud, True)
            
            for x in range(self.cols):
                for y in range(self.rows - longitud + 1):
                    self._evaluate_position(input_matrix_board, heatmap, x, y, longitud, False)

        return self._get_max_coordinate(heatmap, input_matrix_board)

    def _evaluate_position(self, board, heatmap, start_x, start_y, longitud, horizontal):
        casillas_implicadas = []
        atraviesa_impacto = False

        for i in range(longitud):
            cx = start_x + i if horizontal else start_x
            cy = start_y if horizontal else start_y + i
            estado = board[cx][cy]
            
            if estado in ['X', 'H']: 
                return
            if estado == 'O':
                atraviesa_impacto = True
            
            casillas_implicadas.append((cx, cy))

        peso = 50 if atraviesa_impacto else 1
        for cx, cy in casillas_implicadas:
            if board[cx][cy] is None:
                heatmap[cx][cy] += peso

    def _get_max_coordinate(self, heatmap, board):
        max_utilidad = -1
        mejores = []

        for x in range(self.cols):
            for y in range(self.rows):
                if board[x][y] is None:
                    if heatmap[x][y] > max_utilidad:
                        max_utilidad = heatmap[x][y]
                        mejores = [(x, y)]
                    elif heatmap[x][y] == max_utilidad:
                        mejores.append((x, y))

        return random.choice(mejores) if mejores else (0, 0)