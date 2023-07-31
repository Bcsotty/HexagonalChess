import math
from typing import Tuple, Any
import pygame
import os


class Piece(pygame.sprite.Sprite):
    def __init__(self, piece, b_number=1, r_number=1, n_number=1, p_number=1, position="default"):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image(piece + ".png", 0.75)
        match piece:
            case "bB":
                self.piece = "bishop"
                self.color = "black"
                if b_number == 1:
                    self.position = "f11" if position == "default" else position
                elif b_number == 2:
                    self.position = "f10" if position == "default" else position
                elif b_number == 3:
                    self.position = "f9" if position == "default" else position
            case "bK":
                self.piece = "king"
                self.color = "black"
                self.position = "g10" if position == "default" else position
            case "bN":
                self.piece = "knight"
                self.color = "black"
                if n_number == 1:
                    self.position = "e9" if position == "default" else position
                elif n_number == 2:
                    self.position = "g9" if position == "default" else position
            case "bP":
                self.piece = "pawn"
                self.color = "black"
                if p_number == 1:
                    self.position = "c8" if position == "default" else position
                elif p_number == 2:
                    self.position = "d8" if position == "default" else position
                elif p_number == 3:
                    self.position = "e8" if position == "default" else position
                elif p_number == 4:
                    self.position = "f8" if position == "default" else position
                elif p_number == 5:
                    self.position = "g8" if position == "default" else position
                elif p_number == 6:
                    self.position = "h8" if position == "default" else position
                elif p_number == 7:
                    self.position = "i8" if position == "default" else position
            case "bQ":
                self.piece = "queen"
                self.color = "black"
                self.position = "e10" if position == "default" else position
            case "bR":
                self.piece = "rook"
                self.color = "black"
                if r_number == 1:
                    self.position = "d9" if position == "default" else position
                elif r_number == 2:
                    self.position = "h9" if position == "default" else position
            case "wB":
                self.piece = "bishop"
                self.color = "white"
                if b_number == 1:
                    self.position = "f1" if position == "default" else position
                elif b_number == 2:
                    self.position = "f2" if position == "default" else position
                elif b_number == 3:
                    self.position = "f3" if position == "default" else position
            case "wK":
                self.piece = "king"
                self.color = "white"
                self.position = "g1" if position == "default" else position
            case "wN":
                self.piece = "knight"
                self.color = "white"
                if n_number == 1:
                    self.position = "e2" if position == "default" else position
                elif n_number == 2:
                    self.position = "g2" if position == "default" else position
            case "wP":
                self.piece = "pawn"
                self.color = "white"
                if p_number == 1:
                    self.position = "c1" if position == "default" else position
                elif p_number == 2:
                    self.position = "d2" if position == "default" else position
                elif p_number == 3:
                    self.position = "e3" if position == "default" else position
                elif p_number == 4:
                    self.position = "f4" if position == "default" else position
                elif p_number == 5:
                    self.position = "g3" if position == "default" else position
                elif p_number == 6:
                    self.position = "h2" if position == "default" else position
                elif p_number == 7:
                    self.position = "i1" if position == "default" else position
            case "wQ":
                self.piece = "queen"
                self.color = "white"
                self.position = "e1" if position == "default" else position
            case "wR":
                self.piece = "rook"
                self.color = "white"
                if r_number == 1:
                    self.position = "d1" if position == "default" else position
                elif r_number == 2:
                    self.position = "h1" if position == "default" else position
        location = positions[self.position]

        self.rect = pygame.Rect(location, (75.00 + location[0], 75.00 + location[1]))

    def getpos(self):
        return self.rect.center


def load_image(name, scale=1.0):
    fullname = os.path.join(os.path.join((os.path.split(os.path.abspath(__file__)))[0], "images"), name)
    image = pygame.image.load(fullname).convert_alpha()

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pygame.transform.scale(image, size)

    image = image.convert()
    image.set_colorkey(image.get_at((0, 0)), pygame.RLEACCEL)

    return image


def game_loop() -> None:
    """
    Main game loop

    :return: None
    """
    pass


if __name__ == '__main__':
    pygame.init()
