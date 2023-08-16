import utilities
import pygame
from math import sqrt
from piece import Piece, create_default_pieces, create_piece, Pawn
from pygame.locals import *
from settings import Settings
from axial import Axial, position_to_axial, axial_from_string
from event_handler import EventHandler
from copy import deepcopy, copy
import sys


# noinspection PyTypeChecker
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
        self.in_check = False

        self.turn = 1
        self.settings = settings
        self.surface = surface
        self.test_mode = test_mode

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

    def get_king_tile(self, color: int):
        king_tile = None
        for tile in self.tiles.values():
            if tile.piece is None:
                continue

            if tile.piece.color == color and tile.piece.name == "king":
                king_tile = tile
                break

        return king_tile

    def simulate_move(self, new_tile, piece):  # Simulates a move and tells if the move would put team in check
        in_check = False
        tiles = self.tiles
        tile_axial = position_to_axial(new_tile.position)

        piece_current_position = copy(piece.current_position)
        piece_rect_center = copy(piece.rect.center)
        piece_en_passant_possible = False
        new_tile_piece = new_tile.piece
        if new_tile_piece is not None:
            new_tile_piece = new_tile_piece.__deepcopy__()

        dead_pawn_piece = None

        piece.current_position = new_tile.position
        piece.rect.center = new_tile.cartesian_coordinates

        if new_tile.piece is not None:
            self.remove_piece(new_tile.piece)

        if type(piece) == Pawn:
            piece_en_passant_possible = copy(piece.en_passant_possible)
            if piece.en_passant_possible:
                piece.en_passant_possible = False

                addition = -1 if piece.color == 0 else 1
                pawn_axial = axial_from_string(tile_axial.to_string())
                pawn_axial.r = pawn_axial.r + addition
                pawn_tile = tiles.get(pawn_axial.to_string())

                if pawn_tile.piece is not None:
                    if pawn_tile.piece.color != piece.color and pawn_tile.piece.name == "pawn":
                        dead_pawn_piece = pawn_tile.piece.__deepcopy__()
                        self.remove_piece(pawn_tile.piece)
                        pawn_tile.piece = None

        new_tile.piece = piece

        old_tile = tiles.get(position_to_axial(piece.previous_position).to_string())
        old_tile.piece = None

        if self.team_in_check(piece.color):
            in_check = True

        old_tile.piece = piece
        new_tile.piece = new_tile_piece

        if new_tile_piece is not None:
            self.add_piece(new_tile_piece)

        if dead_pawn_piece is not None:
            self.add_piece(dead_pawn_piece)

        piece.en_passant_possible = piece_en_passant_possible

        piece.rect.center = piece_rect_center
        piece.current_position = piece_current_position

        return in_check

    def team_in_check(self, color: int) -> bool:
        king_tile = self.get_king_tile(color)
        if king_tile is None:
            return False

        king_axial = position_to_axial(king_tile.position)

        opponent_color = 1 - color

        color_scalar = 1
        if color == 0:
            color_scalar = -1

        capture_vectors = {  # all possible piece movements for white. Multiply by -1 to get black
            "pawn": [
                (-1, 0),
                (1, -1),
            ],
            "knight": [
                (-3, 1),
                (-2, -1),
                (-1, -2),
                (1, -3),
                (2, -3),
                (3, -2),
                (3, -1),
                (2, 1),
                (1, 2),
                (-1, 3),
                (-2, 3),
                (-3, 2)
            ],
            "bishop": [
                (-2, 1),
                (-1, -1),
                (1, -2),
                (2, -1),
                (1, 1),
                (-1, 2)
            ],
            "rook": [
                (-1, 0),
                (0, -1),
                (1, -1),
                (1, 0),
                (0, 1),
                (-1, 1)
            ],
            "queen": [
                (-1, 0),
                (0, -1),
                (1, -1),
                (1, 0),
                (0, 1),
                (-1, 1),
                (-1, -1),
                (-1, 2),
                (1, 1),
                (1, -2),
                (-2, 1),
                (2, -1)
            ]
        }

        for piece, vectors in capture_vectors.items():
            if piece == "pawn" or piece == "knight" or piece == "king":
                for vector in vectors:
                    new_tile_axial = deepcopy(king_axial)
                    if piece == "pawn":
                        new_tile_axial.add_vector((vector[0] * color_scalar, vector[1] * color_scalar))
                    else:
                        new_tile_axial.add_vector(vector)

                    tile = self.tiles.get(new_tile_axial.to_string())

                    if tile is None:
                        continue

                    if tile.piece is not None:
                        if tile.piece.color == opponent_color and tile.piece.name == piece:
                            return True
            else:
                for vector in vectors:
                    i = 1
                    while True:
                        temp_vector = copy(vector)
                        temp_vector = (temp_vector[0] * i, temp_vector[1] * i)
                        new_tile_axial = deepcopy(king_axial)
                        new_tile_axial.add_vector(temp_vector)

                        tile = self.tiles.get(new_tile_axial.to_string())
                        if tile is None:
                            break

                        if tile.piece is not None:
                            if tile.piece.color == opponent_color and tile.piece.name == piece:
                                return True
                            break

                        i += 1

        return False

    def add_event_handlers(self):
        self.event_handlers = [
            EventHandler(MOUSEBUTTONDOWN, []),
            EventHandler(MOUSEBUTTONUP, []),
            EventHandler(KEYDOWN, [])
        ]

        for handler in self.event_handlers:
            handler.add_subscriber(self, 0.025)

    def update_board(self):
        # Precondition is that the tiles that are legal moves should already have color filter
        # applied
        if self.tiles is None:
            return

        for tile in self.tiles.values():
            tile.draw_tile(self.surface)

    def get_legal_moves(self, piece: Piece):
        return piece.get_piece_moves(self.tiles)

    def get_all_legal_moves(self, color: int):
        legal_moves = []

        for piece in self.pieces:
            if piece.color == color:
                legal_moves.extend(self.get_legal_moves(piece))

        return legal_moves

    def highlight_legal_moves(self):
        legal_moves = self.get_legal_moves(self.piece_selected)

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

        self.highlighted_tiles.extend(legal_moves)

    def reset_highlighted_tiles(self):
        for tile in self.highlighted_tiles:
            tile.reset_filter()

        self.highlighted_tiles = []

    def highlight_king_tile(self):
        king_tile = self.get_king_tile(1 - self.piece_selected.color)

        new_color = pygame.Color(255, 30, 33)

        king_tile.apply_filter(new_color)
        self.highlighted_tiles.append(king_tile)

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

            self.in_check = self.team_in_check(1 - self.piece_selected.color)
            self.reset_highlighted_tiles()
            if self.in_check:
                self.highlight_king_tile()

            self.piece_selected = None

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
        if self.in_check:
            all_team_moves = self.get_all_legal_moves(1 - self.turn)
            if len(all_team_moves) == 0:
                print("CHECKMATE!")
                pygame.quit()
                sys.exit()

        if self.promotion_flag:
            for event in events:
                if event.type == KEYDOWN:
                    self.key_pressed_handler(event)

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

        for tile in self.tiles.values():
            if tile.piece == piece:
                tile.piece = None
                break

    def promote_pawn(self):
        self.promotion_flag = True


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
