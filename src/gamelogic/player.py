from agents.agent import Agent
from gamelogic.board import Board, HitResult

class Player:
    def __init__(self, agent: Agent, board: Board) -> None:
        self.agent = agent
        self.board = board

    def make_move(self, input_matrix_board: list[list[str]]) -> tuple[int, int]:
        return self.agent.make_move(input_matrix_board)

    def get_matrix_board(self) -> list[list[str]]:
        return self.board.get_matrix_board()

    def take_move(self, input_coords: tuple[int, int]) -> HitResult:
        return self.board.take_move(input_coords)
