import utilities
import pygame
from math import sqrt
from piece import Piece, create_pieces


class Board:

    def __init__(self, surface, startX=100, startY=250, scale=1.0):
        self.pieces = self.sprites = None
        self.surface = surface
        self.startX = startX
        self.startY = startY
        utilities.startX = startX
        utilities.startY = startY
        self.scale = scale
        self.initialize()

    def generate_board(self):
        colors = {
            0: pygame.Color(255, 206, 158),
            1: pygame.Color(232, 171, 111),
            2: pygame.Color(209, 139, 71)
        }

        size = 50 * self.scale

        width = size * 2
        height = sqrt(3) * size
        midY = self.startY - height / 2 * 5
        utilities.width = width
        utilities.height = height
        utilities.midY = midY

        for i in range(11):

            rows = 6 + i if i < 6 else 16 - i

            for j in range(rows):
                x = self.startX + 3 / 4 * width * i
                if i < 6:
                    y = self.startY - height / 2 * i + height * j
                    color = colors.get((j + i) % 3)
                else:
                    y = midY + height / 2 * (i - 5) + height * j
                    color = colors.get((7 - i + j) % 3)

                utilities.draw_regular_polygon(self.surface, color, 6, size, (x, y))

    def setup_pieces(self, scale=1.0):
        self.pieces = create_pieces(0, scale)
        self.pieces.extend(create_pieces(1, scale))
        # noinspection PyTypeChecker
        self.sprites = pygame.sprite.Group(self.pieces)

    def initialize(self):
        self.generate_board()
        self.setup_pieces(0.55)

    def update(self, events):
        self.generate_board()
        self.sprites.update()

        for event in events:
            for piece in self.pieces:
                piece.handle_event(event)

        self.sprites.draw(self.surface)
