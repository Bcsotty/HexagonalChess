import os
import pygame
import pickle
from PIL import Image
from math import cos, sin, pi, sqrt


# noinspection PyTypeChecker
def get_piece_image(color: int, piece: str, sprite_scale=1.0):
    """

    Gets the image for the specified piece

    :param color: The color of the piece. 0 for black, 1 for white.
    :param piece: The piece to be chosen
    :param sprite_scale: The scale of the image. Defaults to 1.
    :return: The sprite for the piece
    """
    piece_map = {
        "bishop": 0,
        "king": 1,
        "knight": 2,
        "pawn": 3,
        "queen": 4,
        "rook": 5
    }

    row = piece_map.get(piece)
    if row is None:
        raise Exception("Piece not defined")

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    pieces = Image.open(root_dir + '/images/pieces.png')

    sprite_x = row * 100
    sprite_y = color * 100

    sprite = pieces.crop((sprite_x, sprite_y, sprite_x + 100, sprite_y + 100))

    image = pygame.image.fromstring(sprite.tobytes(), sprite.size, sprite.mode).convert_alpha()

    size = image.get_size()
    size = (size[0] * sprite_scale, size[1] * sprite_scale)
    image = pygame.transform.scale(image, size)

    return image


def draw_regular_polygon(surface: pygame.Surface, color: pygame.Color, vertex_count: int, radius: float,
                         position: (float, float), polygon_width=0):
    # from https://stackoverflow.com/a/57638991/12363073
    n, r = vertex_count, radius
    x, y = position
    pygame.draw.polygon(surface, color, [
        (x + r * cos(2 * pi * i / n), y + r * sin(2 * pi * i / n))
        for i in range(n)
    ], polygon_width)


def position_to_cartesian(board, position: str) -> (float, float):
    file_index, rank = position_to_file_and_rank(position)

    x = board.startX + 3 / 4 * board.tile_width * file_index
    if file_index < 6:
        y = board.startY - board.tile_height * (rank - 6) + board.tile_height / 2 * file_index
    else:
        y = board.midY + board.tile_height * (11 - rank) - board.tile_height / 2 * (file_index - 5)

    return x, y


def position_to_file_and_rank(position: str) -> (int, int):
    file = position[0]
    file_index = ord(file) - 97
    rank = int(position[1:])
    return file_index, rank


def clamp(value, add, maximum, minimum=0):
    if value + add > maximum:
        return maximum
    if value + add < minimum:
        return minimum

    return int(value + add)


def save_object(obj: object, file_name: str):
    with open(file_name, 'wb') as file:
        pickle.dump(obj, file)


def load_object(file_name: str) -> object | None:
    try:
        with open(file_name, 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        return None
