import utilities
import pygame
from math import sqrt
from piece import Piece, create_pieces
from pygame.locals import *


class Board:

    def __init__(self, surface, startX=100, startY=250, scale=1.0):
        self.pieces = None
        self.sprites = None
        self.tiles = None
        self.center = None
        self.piece_selected = None
        self.last_piece_moved = None
        self.highlighted_tiles = []

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
        self.center = (self.startX + 3 / 4 * width * 5, self.startY - height / 2 * 5 + height * 5)

        utilities.width = width
        utilities.height = height
        utilities.midY = midY
        utilities.center = self.center
        utilities.scale = self.scale

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
                        utilities.position_to_axial(tile.position): tile
                    }
                else:
                    self.tiles[utilities.position_to_axial(tile.position)] = tile

                tile.draw_tile(self.surface)

    def setup_pieces(self, scale=1.0):
        self.pieces = create_pieces(0, self, scale)
        self.pieces.extend(create_pieces(1, self, scale))

        for piece in self.pieces:
            axial = utilities.position_to_axial(piece.current_position)
            tile = self.tiles.get(axial)
            tile.piece = piece
        # noinspection PyTypeChecker
        self.sprites = pygame.sprite.Group(self.pieces)

    def add_piece(self, *pieces: Piece):
        for piece in pieces:
            axial = utilities.position_to_axial(piece.current_position)
            tile = self.tiles.get(axial)
            tile.piece = piece

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
        legal_moves = self.piece_selected.get_piece_moves(self.tiles)

        for tile in legal_moves:
            highlight = (-255, 255, -255)

            new_color = (utilities.clamp(highlight[0], tile.color.r, 255),
                         utilities.clamp(highlight[1], tile.color.g, 255),
                         utilities.clamp(highlight[2], tile.color.b, 255))

            tile.apply_filter(pygame.color.Color(new_color[0], new_color[1], new_color[2]))

        current_tile = self.tiles.get(utilities.position_to_axial(self.piece_selected.current_position))
        current_tile.piece = self.piece_selected

        current_tile.apply_filter(pygame.color.Color(255, 0, 0))

        legal_moves.append(current_tile)

        self.highlighted_tiles = legal_moves

    def reset_highlighted_tiles(self):
        for tile in self.highlighted_tiles:
            tile.reset_filter()

        self.highlighted_tiles = []

    def update(self, events) -> int:
        if self.sprites is None or self.pieces is None:
            return self.turn

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if self.piece_selected is None:
                    for piece in self.pieces:
                        if piece.color != self.turn:
                            continue
                        self.piece_selected = piece.handle_event(event)
                        if self.piece_selected is not None:
                            self.generate_legal_moves()
                            break

            elif event.type == MOUSEBUTTONUP:
                if self.piece_selected is not None:
                    for piece in self.pieces:
                        valid_move = piece.handle_event(event)
                        if valid_move:
                            self.turn = 1 - self.turn
                            self.last_piece_moved = self.piece_selected
                            break

                    self.piece_selected = None
                    self.reset_highlighted_tiles()

        self.sprites.update(self.tiles)
        self.update_board()
        self.sprites.draw(self.surface)

        return self.turn

    def remove_piece(self, piece: Piece):
        self.pieces.remove(piece)
        self.sprites.remove(piece)


class Tile:
    def __init__(self, color: pygame.color.Color, position: str, coordinates: (float, float), size: float, piece=None):
        self.color = color
        self.displayed_color = color
        self.position = position
        self.cartesian_coordinates = coordinates
        self.piece = piece
        self.size = size

    def draw_tile(self, surface: pygame.surface.Surface):
        utilities.draw_regular_polygon(surface, self.displayed_color, 6, self.size, self.cartesian_coordinates)

    def apply_filter(self, color: pygame.color.Color):
        self.displayed_color = color

    def reset_filter(self):
        self.displayed_color = self.color
