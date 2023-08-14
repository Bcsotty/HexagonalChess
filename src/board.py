import utilities
import pygame
from math import sqrt
from piece import Piece, create_default_pieces
from pygame.locals import *
from settings import Settings
from axial import Axial, position_to_axial
from event_handler import EventHandler


class Board:

    def __init__(self, surface: pygame.Surface, settings: Settings, startX=0, startY=0, scale=1.0):
        self.event_handlers: list[EventHandler] | None = None
        self.tile_height = None
        self.tile_width = None
        self.pieces = None
        self.sprites = None
        self.tiles = None
        self.center = None
        self.piece_selected = None
        self.last_piece_moved = None
        self.highlighted_tiles = []

        self.turn = 1
        self.settings = settings
        self.surface = surface

        self.startX = startX
        self.startY = startY
        self.midY = None
        self.scale = scale

    def generate_default_board(self):
        colors = {
            0: pygame.Color(255, 206, 158),
            1: pygame.Color(232, 171, 111),
            2: pygame.Color(209, 139, 71)
        }

        size = 50 * self.scale

        self.tile_width = size * 2
        self.tile_height = sqrt(3) * size
        self.midY = self.startY - self.tile_height / 2 * 5
        self.center = (self.startX + 3 / 4 * self.tile_width * 5, self.startY - self.tile_height / 2 * 5 +
                       self.tile_height * 5)

        for i in range(11):

            rows = 6 + i if i < 6 else 16 - i

            for j in range(rows):
                x = self.startX + 3 / 4 * self.tile_width * i
                if i < 6:
                    y = self.startY - self.tile_height / 2 * i + self.tile_height * j
                    color = colors.get((j + i) % 3)
                else:
                    y = self.midY + self.tile_height / 2 * (i - 5) + self.tile_height * j
                    color = colors.get((7 - i + j) % 3)

                tile = Tile(color, chr(i + 97) + str(rows - j), (x, y), size)

                if self.tiles is None:
                    self.tiles = {
                        position_to_axial(tile.position).to_string(): tile
                    }
                else:
                    self.tiles[position_to_axial(tile.position).to_string()] = tile

                tile.draw_tile(self.surface)

    def setup_pieces(self, scale=1.0):
        self.pieces = create_default_pieces(0, self, scale)
        self.pieces.extend(create_default_pieces(1, self, scale))

        for piece in self.pieces:
            axial = position_to_axial(piece.current_position)
            tile = self.tiles.get(axial.to_string())
            tile.piece = piece

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
        self.setup_pieces(self.settings.dimensions[0] * 0.0006875)

        for handler in self.event_handlers:
            if handler.event_type == MOUSEBUTTONDOWN:
                handler.add_subscriber(self)

    def add_event_handlers(self, *event_handlers: EventHandler):
        if not self.event_handlers:
            self.event_handlers = [event_handler for event_handler in event_handlers]
        else:
            self.event_handlers.extend(event_handlers)

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

        current_tile = self.tiles.get(position_to_axial(self.piece_selected.current_position).to_string())
        current_tile.piece = self.piece_selected

        current_tile.apply_filter(pygame.color.Color(255, 0, 0))

        legal_moves.append(current_tile)

        self.highlighted_tiles = legal_moves

    def reset_highlighted_tiles(self):
        for tile in self.highlighted_tiles:
            tile.reset_filter()

        self.highlighted_tiles = []

    def mouse_button_down_handler(self, event: pygame.event.Event):
        if self.piece_selected is None:
            for piece in self.pieces:
                if piece.color != self.turn:
                    continue

                self.piece_selected = piece.handle_event(event)

                if self.piece_selected is not None:
                    self.generate_legal_moves()
                    break

    def update(self, events: list[pygame.event.Event]) -> None:
        if self.sprites is None or self.pieces is None:
            return


        for event in events:
            for event_handler in self.event_handlers:
                if event.type == event_handler.event_type:
                    event_handler.event_triggered(event)
                    break


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
