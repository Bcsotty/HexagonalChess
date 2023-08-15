import utilities
import pygame
from math import sqrt
from piece import Piece, create_default_pieces, create_piece
from pygame.locals import *
from settings import Settings
from axial import Axial, position_to_axial
from event_handler import EventHandler


class Board:

    def __init__(self, surface: pygame.Surface, settings: Settings, test_mode=False):
        self.piece_scale: float = 0.
        self.event_handlers: list[EventHandler] | None = None
        self.tile_height = None
        self.tile_width = None
        self.pieces: list[Piece] | None = None
        self.sprites = None
        self.tiles: dict[str, Tile] | None = None
        self.center = None
        self.piece_selected: Piece | None = None
        self.last_piece_moved: Piece | None = None
        self.midY = None
        self.promotion_flag = False
        self.highlighted_tiles = []
        self.test_mode = test_mode

        self.turn = 1
        self.settings = settings
        self.surface = surface

        #  Determining scale, x, and y for the board
        self.scale = settings.dimensions[0] * 0.0009375
        self.piece_scale = settings.dimensions[0] * 0.0006875
        half_board_width = 50 * self.scale * 16 / 2
        self.startX = settings.dimensions[0] / 2 - half_board_width
        self.startY = (settings.dimensions[0] / 100 - 6) * 30 + 190

    def generate_blank_board(self):
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
            axial = position_to_axial(piece.current_position)
            tile = self.tiles.get(axial.to_string())
            tile.piece = piece

        if self.pieces is None:
            self.pieces = [piece for piece in pieces]
            self.sprites = pygame.sprite.Group(self.pieces)
        else:
            self.pieces.extend(pieces)
            self.sprites.add(pieces)

    def start_game(self):
        self.generate_blank_board()
        self.setup_pieces(self.piece_scale)
        self.add_event_handlers()

    def add_event_handlers(self):
        self.event_handlers = [
            EventHandler(MOUSEBUTTONDOWN, []),
            EventHandler(MOUSEBUTTONUP, []),
            EventHandler(KEYDOWN, [])
        ]

        for handler in self.event_handlers:
            handler.add_subscriber(self)

    def update_board(self):
        # Precondition is that the tiles that are legal moves should already have color filter
        # applied
        if self.tiles is None:
            return

        for tile in self.tiles.values():
            tile.draw_tile(self.surface)

    def highlight_legal_moves(self):
        legal_moves = self.piece_selected.get_piece_moves(self.tiles)

        for tile in legal_moves:
            highlight = self.settings.highlight

            new_color = (utilities.clamp(highlight[0], tile.color.r, 255),
                         utilities.clamp(highlight[1], tile.color.g, 255),
                         utilities.clamp(highlight[2], tile.color.b, 255))

            tile.apply_filter(pygame.color.Color(new_color[0], new_color[1], new_color[2]))

        current_tile = self.tiles.get(position_to_axial(self.piece_selected.current_position).to_string())
        current_tile.piece = self.piece_selected

        current_color = (utilities.clamp(100, current_tile.color.r, 255),
                         utilities.clamp(-60, current_tile.color.g, 255),
                         utilities.clamp(-60, current_tile.color.b, 255))

        current_tile.apply_filter(pygame.color.Color(current_color[0], current_color[1], current_color[2]))

        legal_moves.append(current_tile)

        self.highlighted_tiles = legal_moves

    def reset_highlighted_tiles(self):
        for tile in self.highlighted_tiles:
            tile.reset_filter()

        self.highlighted_tiles = []

    def mouse_button_down_handler(self, event: pygame.event.Event):
        if self.pieces is None:
            return

        if self.piece_selected is None:
            for piece in self.pieces:
                if not self.test_mode:
                    if piece.color != self.turn:
                        continue

                self.piece_selected = piece.mouse_button_down_handler(event)

                if self.piece_selected is not None:
                    self.highlight_legal_moves()
                    break

    def mouse_button_up_handler(self, event: pygame.event.Event):
        if self.piece_selected is not None:
            for piece in self.pieces:
                valid_move = piece.mouse_button_up_handler(event)
                if valid_move:
                    self.turn = 1 - self.turn
                    self.last_piece_moved = self.piece_selected
                    break

            self.piece_selected = None
            self.reset_highlighted_tiles()

    def key_pressed_handler(self, event: pygame.event.Event):
        if not self.promotion_flag:
            return

        key = chr(event.key)
        color = self.last_piece_moved.color
        position = self.last_piece_moved.current_position
        scale = self.piece_scale

        match key:
            case "q":
                piece = "queen"

            case "r":
                piece = "rook"

            case "b":
                piece = "bishop"

            case "n":
                piece = "knight"

            case _:
                return

        new_piece = create_piece(color, piece, position, self, scale)

        tile = self.tiles.get(position_to_axial(position).to_string())
        tile.piece = new_piece

        self.pieces.remove(self.last_piece_moved)
        self.sprites.remove(self.last_piece_moved)

        self.pieces.append(new_piece)
        self.sprites.add(new_piece)

        self.promotion_flag = False

    def update(self, events: list[pygame.event.Event]) -> None:
        if self.promotion_flag:
            for event in events:
                if event.type == KEYDOWN:
                    self.key_pressed_handler(event)

        else:
            for event in events:
                for event_handler in self.event_handlers:
                    if event.type == event_handler.event_type:
                        event_handler.event_triggered(event)
                        break

        if self.sprites is not None:
            self.sprites.update(self.tiles)
            self.update_board()
            self.sprites.draw(self.surface)
        else:
            self.update_board()

    def remove_piece(self, piece: Piece):
        self.pieces.remove(piece)
        self.sprites.remove(piece)

    def promote_pawn(self, piece: Piece):
        # Handles the promotion of a pawn. Need to prompt user for piece (simple form of add flag to update and add key
        # handlers for the pieces) followed by creating the piece at the same location as the pawn, then remove the pawn
        # from the tile, the pieces list, and the groups list
        self.promotion_flag = True
        pass


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
