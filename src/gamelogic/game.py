from gamelogic.player import Player
from gamelogic.board import HitResult

class Game:
    ...
    def __init__(self, player_a: Player, player_b: Player) -> None:
        self.player_a = player_a
        self.player_b = player_b
        self.current_player =  self.player_a
        self.opponent_player = self.player_b

    def switch_player(self) -> None:
        if self.current_player == self.player_a:
            self.current_player  = self.player_b
            self.opponent_player = self.player_a
        else:
            self.current_player  = self.player_a
            self.opponent_player = self.player_b

    def take_next_move(self) -> bool:
        opponent_matrix = self.opponent_player.get_matrix_board()
        attack_cords = self.player_a.make_move(opponent_matrix)
        attack_result = self.opponent_player.take_move(attack_cords)

        match attack_result:
            case HitResult.MISS | HitResult.HIT:
                self.switch_player()
                return True
            case HitResult.DEFEAT:
                return False
