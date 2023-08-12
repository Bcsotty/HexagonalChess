import utilities
import pygame
from math import sqrt
from piece import Piece, create_pieces
from pygame.locals import *


class Board:

    def __init__(self, surface, startX=100, startY=250, scale=1.0):
        self.pieces = self.sprites = self.tiles = self.center = self.piece_selected = None
        self.turn = 1
        self.surface = surface
        self.startX = startX
        self.startY = startY
        utilities.startX = startX
        utilities.startY = startY
        self.scale = scale

    def generate_default_board(self):
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

        self.center = (self.startX + 3 / 4 * width * 5, self.startY - height / 2 * 5 + height * 5)

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

                tile = Tile(color, chr(i + 97) + str(rows - j), (x, y), size)

                if self.tiles is None:
                    self.tiles = {
                        self.pixel_to_axial(tile.cartesian_coordinates): tile
                    }
                else:
                    self.tiles[self.pixel_to_axial(tile.cartesian_coordinates)] = tile

                tile.draw_tile(self.surface)

    def setup_pieces(self, scale=1.0):
        self.pieces = create_pieces(0, scale)
        self.pieces.extend(create_pieces(1, scale))
        # noinspection PyTypeChecker
        self.sprites = pygame.sprite.Group(self.pieces)

    def add_piece(self, *pieces: Piece):
        if self.pieces is None:
            self.pieces = [piece for piece in pieces]
            self.sprites = pygame.sprite.Group(self.pieces)
        else:
            self.pieces.extend(pieces)
            self.sprites.add(pieces)

    def start_game(self):
        self.generate_default_board()
        self.setup_pieces(0.55)

    def update_board(self):
        # Precondition is that the tiles that are legal moves should already have color filter
        # applied
        if self.tiles is None:
            return

        for tile in self.tiles.values():
            tile.draw_tile(self.surface)

    def generate_legal_moves(self):
        pawn_moves = []

        for piece in self.pieces:
            if piece.name == "pawn":
                pawn_moves.append(piece.get_piece_moves(self.tiles))

    def update(self, events) -> int:
        if self.sprites is None or self.pieces is None:
            return self.turn

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.piece_selected is None:
                    for piece in self.pieces:
                        self.piece_selected = piece.handle_event(event, self.tiles)
                        if self.piece_selected is not None:
                            break

                if self.piece_selected is not None:
                    self.generate_legal_moves()

            elif event.type == MOUSEBUTTONUP:
                if self.piece_selected is not None:
                    for piece in self.pieces:
                        piece.handle_event(event, self.tiles)
                    self.piece_selected = None

        self.sprites.update(self.tiles)
        self.update_board()
        self.sprites.draw(self.surface)

    def pixel_to_axial(self, point: (float, float)):
        x = point[0] - self.center[0]
        y = point[1] - self.center[1]
        q = (2 / 3 * x) / (50 * self.scale)
        r = (-1 / 3 * x + sqrt(3) / 3 * y) / (50 * self.scale)
        return utilities.axial_round((q, r))


class Tile:
    def __init__(self, color: pygame.color.Color, position: str, coordinates: (float, float), size: float):
        self.color = color
        self.position = position
        self.cartesian_coordinates = coordinates

        self.size = size

        self.bbox = pygame.rect.Rect(coordinates[0] - size / 2, coordinates[1] - sqrt(3) * size / 2, size, sqrt(3) *
                                     size)

    def draw_tile(self, surface: pygame.surface.Surface):
        utilities.draw_regular_polygon(surface, self.color, 6, self.size, self.cartesian_coordinates)
