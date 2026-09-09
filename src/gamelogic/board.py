class Board:
    ...
    def __init__(self, ship_coords: tuple[tuple[int, str, int]]) -> None:
        self.get_matrix_board = list()

    def get_matrix_board(self) -> list[list[str]]:
        return self.matrix_board
