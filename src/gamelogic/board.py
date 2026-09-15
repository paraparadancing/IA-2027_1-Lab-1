from __future__ import annotations
from enum import Enum, auto

LONGITUD = 10
ALTURA   = 10

class Board:
    def __init__(self, ship_positions: tuple[Ship]) -> None:
        if len(ship_positions) > 0:
            self.matrix_board = [
                [None for j in range(ALTURA)] for i in range(LONGITUD)
            ]
            (
                self.used_boxes,
                self.afloat_ships) = (
                place_ships(ship_positions)
            )
        else:
            raise ValueError("El tablero debe contener al menos un barco.")

    def get_matrix_board(self) -> list[list[str]]:
        return self.matrix_board
    
    def take_move(self, input_coords: tuple[int, int]) -> HitResult:
        hit_result = self.used_boxes.get(input_coords)
        if hit_result is None:
            self.mark_missed_box(input_coords)
            return HitResult.MISS
        else:
            self.used_boxes.pop(input_coords)
            hit_result.take_impact()
            if hit_result.is_destroyed():
                self.mark_sunken_ship(hit_result)
                self.afloat_ships.remove(hit_result)
                if len(self.afloat_ships) == 0:
                    return HitResult.DEFEAT
            else:
                self.mark_hit_box(input_coords)
            return HitResult.HIT
    
    def mark_missed_box(self, input_coords: tuple[int, int]) -> None:
        self.matrix_board[input_coords[0]][input_coords[1]] = 'X'

    def mark_hit_box(self, input_coords: tuple[int, int]) -> None:
        self.matrix_board[input_coords[0]][input_coords[1]] = 'O'

    def mark_sunken_ship(self, input_ship: Ship) -> None:
        for box in input_ship.get_boxes():
            self.matrix_board[box[0]][box[1]] = 'H'

class Ship:
    def __init__(self, length: int, width: int, position: tuple[int, int]) -> None:
        if length > 0:
            self.length = length
        else:
            raise ValueError("La longitud de barco debe ser mayor a 0.")

        if width > 0:
            self.width = width
        else:
            raise ValueError("La amplitud de barco debe ser mayor a 0.")

        self.remaining_cells = length * width

        if all(coord >= 0 for coord in position):
            self.position = position
        else:
            raise ValueError("Las coordenadas deben ser iguales o mayores a 0.")

        self.boxes = tuple(
            (position[0] + w, position[1] + l) for w in range(width) for l in range(length)
        )

    def get_boxes(self) -> tuple[tuple[int, int]]:
        return self.boxes

    def take_impact(self) -> None:
        self.remaining_cells -= 1

    def is_destroyed(self) -> bool:
        return self.remaining_cells <= 0

class HitResult(Enum):
    MISS = auto()
    HIT = auto()
    DEFEAT = auto()

def place_ships(ships: tuple[Ship]) -> (
        tuple[dict[tuple[int, int], Ship], list[Ship]]
    ):
    boxes: dict[tuple[int, int], Ship] = dict()
    placed_ships: list[Ship] = list()

    for ship in ships:
        for box in ship.get_boxes():
            if ship.box[0] >= LONGITUD or ship.box[1] >= ALTURA:
                raise ValueError("El barco se sale del tablero.")

            result = boxes.get((ship.box[0], ship.box[1]))

            if result is None:
                boxes[(ship.box[0], ship.box[1])] = ship
            else:
                raise ValueError("Hay empalme entre barcos.")
        placed_ships.append(ship)

    return boxes, placed_ships
