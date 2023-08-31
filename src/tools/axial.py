from src.tools.utilities import position_to_file_and_rank
from math import sqrt


class Axial:
    def __init__(self, q: int, r: int):
        self.q = q
        self.r = r

    def to_string(self) -> str:
        return f"{self.q},{self.r}"

    def add_vector(self, vector: (int, int)) -> None:
        self.q += vector[0]
        self.r += vector[1]


def axial_from_string(string: str) -> Axial:
    q = int(string[:string.find(",")])
    r = int(string[string.find(",") + 1:])
    return Axial(q, r)


def pixel_to_axial(board, point: (float, float)) -> Axial:
    x = point[0] - board.center[0]
    y = point[1] - board.center[1]
    q = (2 / 3 * x) / (50 * board.scale)
    r = (-1 / 3 * x + sqrt(3) / 3 * y) / (50 * board.scale)
    return axial_round((q, r))


def axial_round(point: (float, float)) -> Axial:
    x, y = point
    x_grid = round(x)
    y_grid = round(y)

    x -= x_grid
    y -= y_grid

    if abs(x) >= abs(y):
        return Axial(x_grid + round(x + 0.5 * y), y_grid)
    else:
        return Axial(x_grid, y_grid + round(y + 0.5 * x))


def position_to_axial(position: str) -> Axial:
    file_index, rank = position_to_file_and_rank(position)

    x = -5 + file_index
    y = 6 - rank if file_index < 6 else 6 - (file_index - 5) - rank

    return Axial(x, y)
