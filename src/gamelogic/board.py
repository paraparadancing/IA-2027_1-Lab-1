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
        
        if all(position) >= 0:
            self.position = position
        else:
            raise ValueError("Las coordenadas deben ser iguales o mayores a 0.")

    def get_position(self) -> tuple[int, int]:
        return self.position
    
    def get_length(self) -> int:
        return self.length

    def get_width(self) -> int:
        return self.width

def place_ships(ships: tuple[Ship]) -> (
        tuple[dict[tuple[int, int], Ship], list[Ship]]
    ):
    boxes: dict[tuple[int, int], Ship] = dict()
    placed_ships: list[Ship] = list()

    for ship in ships:
        for w in range(ship.get_width()):
            for l in range(ship.get_length()):
                target_x = ship.get_position()[0] + w
                target_y = ship.get_position()[1] + l

                if target_x >= LONGITUD or target_y >= ALTURA:
                    raise ValueError("El barco se sale del tablero.")

                result = boxes.get((target_x, target_y))

                if result is None:
                    boxes[(target_x, target_y)] = ship
                    placed_ships.append(ship)
                else:
                    raise ValueError("Hay empalme entre barcos.")

    return boxes, placed_ships
