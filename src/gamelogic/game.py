from src.gamelogic.player import Player

class Game:
    ...
    def __init__(self, player_a: Player, player_b: Player) -> None:
        self.player_a = player_a
        self.player_b = player_b
        self.current_player = player_a
        self.opponent_player = player_b

    def switch_player(self) -> None:
        if self.current_player == self.player_a:
            self.current_player  = self.player_b
            self.opponent_player = self.player_a
        else:
            self.current_player  = self.player_a
            self.opponent_player = self.player_b

    def take_next_move(self) -> bool:
        self.opponent_board = self.opponent_player.get_matrix_board()
        self.attack_cords = self.player_a.make_move()
