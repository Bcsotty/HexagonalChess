import os
import pygame
from PIL import Image
from math import cos, sin, pi


def load_image_from_disk(imagePath: str, scale=1.0):
    """

    Loads an image from disk

    :param imagePath: Path to the image
    :param scale: Scale to load the image at
    :return: The pygame image surface
    """
    fullname = os.path.join(os.path.join((os.path.split(os.path.abspath(__file__)))[0], "images"), imagePath)
    image = pygame.image.load(fullname).convert_alpha()

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pygame.transform.scale(image, size)

    image = image.convert()
    image.set_colorkey(image.get_at((0, 0)), pygame.RLEACCEL)

    return image


# noinspection PyTypeChecker
def get_piece_image(color: int, piece: str, scale=1.0):
    """

    Gets the image for the specified piece

    :param color: The color of the piece. 0 for black, 1 for white.
    :param piece: The piece to be chosen
    :param scale: The scale of the image. Defaults to 1.
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

    pieces = Image.open('images/pieces.png')

    sprite_x = row * 100
    sprite_y = color * 100

    sprite = pieces.crop((sprite_x, sprite_y, sprite_x + 100, sprite_y + 100))

    image = pygame.image.fromstring(sprite.tobytes(), sprite.size, sprite.mode).convert_alpha()

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pygame.transform.scale(image, size)

    return image


def draw_regular_polygon(surface, color, vertex_count, radius, position, width=0):
    # from https://stackoverflow.com/a/57638991/12363073
    n, r = vertex_count, radius
    x, y = position
    pygame.draw.polygon(surface, color, [
        (x + r * cos(2 * pi * i / n), y + r * sin(2 * pi * i / n))
        for i in range(n)
    ], width)

def pil_image_to_surface(pilImage):
    return pygame.image.fromstring(pilImage.tobytes(), pilImage.size, pilImage.mode).convert()
