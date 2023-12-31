import pygame
from utilities import get_piece_image, position_to_cartesian, position_to_file_and_rank
from axial import position_to_axial, Axial, pixel_to_axial, axial_from_string
from pygame.locals import *
from abc import abstractmethod, ABC
from copy import copy

positions = {
    "0queen": "e10",
    "0king": "g10",
    "0bishop": ["f11", "f10", "f9"],
    "0knight": ["d9", "h9"],
    "0rook": ["c8", "i8"],
    "0pawn": ["b7", "c7", "d7", "e7", "f7", "g7", "h7", "i7", "j7"],
    "1queen": "e1",
    "1king": "g1",
    "1bishop": ["f1", "f2", "f3"],
    "1knight": ["d1", "h1"],
    "1rook": ["c1", "i1"],
    "1pawn": ["b1", "c2", "d3", "e4", "f5", "g4", "h3", "i2", "j1"]
}


class Piece(pygame.sprite.Sprite, ABC):
    """

    Piece sprite

    """

    def __init__(self, color: int, piece: str, position: str, board, scale=1.0):
        """
        :param color: Color of the piece. 0 for black, 1 for white
        :param piece: The piece name
        :param position: The rank and file to be placed at. (a7, f2, etc.)
        """

        super().__init__()

        self.image = get_piece_image(color, piece, scale)
        self.name = piece
        self.color = color
        self.current_position = position
        self.previous_position = position
        self.rect = self.image.get_rect()
        self.rect.center = position_to_cartesian(board, position)
        self.dragging = False
        self.board = board

    def update(self, tiles: dict):
        if self.dragging:
            self.rect.center = pygame.mouse.get_pos()

            for axial, tile in tiles.items():
                if pixel_to_axial(self.board, self.rect.center) == axial:
                    self.current_position = tile.position
                    break

    def mouse_button_down_handler(self, event: pygame.event.Event):
        if self.rect.collidepoint(event.pos):
            self.previous_position = self.current_position
            self.dragging = True
            return self

    def mouse_button_up_handler(self, event: pygame.event.Event) -> bool:
        tiles = self.board.tiles

        if self.dragging:
            found_tile = None

            for tile_axial, tile in tiles.items():
                if (pixel_to_axial(self.board, self.rect.center).to_string() == tile_axial and
                        (tile in self.board.highlighted_tiles or self.board.test_mode) and
                        tile.position != self.previous_position):

                    self.board.move_piece(tile, self)
                    found_tile = True
                    break

            if not found_tile:
                self.current_position = self.previous_position
                self.rect.center = position_to_cartesian(self.board, self.current_position)

            self.dragging = False
            return found_tile

        return False

    def is_legal_move(self, tile) -> bool:
        # Check if the piece (self) moving to the tile is a legal move (moving piece doesn't put our king in check)
        in_check = self.board.simulate_move(tile, self)
        if in_check:
            return False
        return True

    def configure_copy(self, piece_copy):
        piece_copy.dragging = copy(self.dragging)
        piece_copy.previous_position = copy(self.previous_position)
        piece_copy.current_position = copy(self.current_position)
        piece_copy.rect = copy(self.rect)
        return piece_copy

    @abstractmethod
    def get_piece_moves(self, tiles: dict):
        pass

    @abstractmethod
    def __deepcopy__(self, memodict=None, piece_copy=None):
        if memodict is None:
            memodict = {}


class Pawn(Piece):
    def __init__(self, color: int, position: str, board, scale=1.0):
        super().__init__(color, "pawn", position, board, scale)
        self.en_passant_possible = False

    def get_piece_moves(self, tiles: dict) -> list:
        legal_moves = []
        possible_moves = []
        axial = position_to_axial(self.current_position)

        movement_vectors = [
                (-1, 0),  # Capture left
                (1, -1),  # Capture right
                (0, -1),  # Forward 1
                (0, -2),  # Forward 2 (Starting spot)
            ]

        color_scalar = 1

        if self.color == 0:
            color_scalar = -1

        start_locations = positions.get(str(self.color) + "pawn")

        for vector in movement_vectors:
            if self.current_position not in start_locations:
                if vector[1] == -2:
                    continue

            new_axial = (axial.q + vector[0] * color_scalar, axial.r + vector[1] * color_scalar)

            tile = tiles.get(Axial(new_axial[0], new_axial[1]).to_string())
            if tile is None:
                continue

            if not (vector[0] == 0):
                piece_moved = self.board.last_piece_moved

                if piece_moved is not None:  # Handling en passant conditions
                    if piece_moved.name == "pawn":
                        if piece_moved.previous_position in positions.get(str(piece_moved.color) + "pawn"):
                            piece_axial = position_to_axial(piece_moved.current_position)

                            if (new_axial[0] == piece_axial.q) and (
                                    new_axial[1] + color_scalar == piece_axial.r):
                                self.en_passant_possible = True
                                possible_moves.append(tile)
                                continue

                if tile.piece is None:
                    continue

                if tile.piece.color == self.color:
                    continue
            else:
                if tile.piece is not None:
                    break

            possible_moves.append(tile)

        for tile in possible_moves:  # Check for checkmates, etc. here
            legal_move = super().is_legal_move(tile)
            if legal_move:
                legal_moves.append(tile)

        return legal_moves

    def mouse_button_up_handler(self, event: pygame.event.Event) -> bool:
        valid_move = super().mouse_button_up_handler(event)

        if valid_move:
            axial = position_to_axial(self.current_position)
            axial.r = axial.r - 1
            if self.board.tiles.get(axial.to_string()) is None:
                self.board.promote_pawn()

        return valid_move

    def __deepcopy__(self, memodict=None, piece_copy=None):
        if memodict is None:
            memodict = {}

        piece_copy = Pawn(copy(self.color), copy(self.current_position), self.board, self.board.piece_scale)

        piece_copy.en_passant_possible = copy(self.en_passant_possible)
        return super().configure_copy(piece_copy=piece_copy)


class Queen(Piece):
    def __init__(self, color: int, position: str, board, scale=1.0):
        super().__init__(color, "queen", position, board, scale)

    def get_piece_moves(self, tiles: dict) -> list:
        legal_moves = []
        possible_moves = []
        axial = position_to_axial(self.current_position)

        movement_vectors = [
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

        color_scalar = 1

        if self.color == 0:
            color_scalar = -1

        for vector in movement_vectors:
            i = 1
            while True:
                new_axial = (axial.q + vector[0] * color_scalar * i, axial.r + vector[1] * color_scalar * i)

                tile = tiles.get(Axial(new_axial[0], new_axial[1]).to_string())
                if tile is None:
                    break

                if tile.piece is not None:
                    if tile.piece.color != self.color:
                        possible_moves.append(tile)
                    break

                possible_moves.append(tile)
                i += 1

        for tile in possible_moves:  # Check for checkmates, etc. here
            legal_move = super().is_legal_move(tile)
            if legal_move:
                legal_moves.append(tile)

        return legal_moves

    def __deepcopy__(self, memodict=None, piece_copy=None):
        if memodict is None:
            memodict = {}

        piece_copy = Queen(copy(self.color), copy(self.current_position), self.board, self.board.piece_scale)

        return super().configure_copy(piece_copy=piece_copy)


class King(Piece):
    def __init__(self, color: int, position: str, board, scale=1.0):
        super().__init__(color, "king", position, board, scale)

    def get_piece_moves(self, tiles: dict) -> list:
        legal_moves = []
        possible_moves = []
        axial = position_to_axial(self.current_position)

        movement_vectors = [
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

        color_scalar = 1

        if self.color == 0:
            color_scalar = -1

        for vector in movement_vectors:
            new_axial = (axial.q + vector[0] * color_scalar, axial.r + vector[1] * color_scalar)

            tile = tiles.get(Axial(new_axial[0], new_axial[1]).to_string())
            if tile is None:
                continue

            if tile.piece is not None:
                if tile.piece.color != self.color:
                    possible_moves.append(tile)
                continue

            possible_moves.append(tile)

        for tile in possible_moves:  # Check for checkmates, etc. here
            legal_move = super().is_legal_move(tile)
            if legal_move:
                legal_moves.append(tile)

        return legal_moves

    def __deepcopy__(self, memodict=None, piece_copy=None):
        if memodict is None:
            memodict = {}

        piece_copy = King(copy(self.color), copy(self.current_position), self.board, self.board.piece_scale)

        return super().configure_copy(piece_copy=piece_copy)


class Rook(Piece):
    def __init__(self, color: int, position: str, board, scale=1.0):
        super().__init__(color, "rook", position, board, scale)

    def get_piece_moves(self, tiles: dict) -> list:
        legal_moves = []
        possible_moves = []
        axial = position_to_axial(self.current_position)

        movement_vectors = [
            (-1, 0),
            (0, -1),
            (1, -1),
            (1, 0),
            (0, 1),
            (-1, 1),
        ]

        color_scalar = 1

        if self.color == 0:
            color_scalar = -1

        for vector in movement_vectors:
            i = 1
            while True:
                new_axial = (axial.q + vector[0] * color_scalar * i, axial.r + vector[1] * color_scalar * i)

                tile = tiles.get(Axial(new_axial[0], new_axial[1]).to_string())
                if tile is None:
                    break

                if tile.piece is not None:
                    if tile.piece.color != self.color:
                        possible_moves.append(tile)
                    break

                possible_moves.append(tile)
                i += 1

        for tile in possible_moves:  # Check for checkmates, etc. here
            legal_move = super().is_legal_move(tile)
            if legal_move:
                legal_moves.append(tile)

        return legal_moves

    def __deepcopy__(self, memodict=None, piece_copy=None):
        if memodict is None:
            memodict = {}

        piece_copy = Rook(copy(self.color), copy(self.current_position), self.board, self.board.piece_scale)

        return super().configure_copy(piece_copy=piece_copy)


class Knight(Piece):
    def __init__(self, color: int, position: str, board, scale=1.0):
        super().__init__(color, "knight", position, board, scale)

    def get_piece_moves(self, tiles: dict) -> list:
        legal_moves = []
        possible_moves = []
        axial = position_to_axial(self.current_position)

        movement_vectors = [
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
        ]

        color_scalar = 1

        if self.color == 0:
            color_scalar = -1

        for vector in movement_vectors:
            new_axial = (axial.q + vector[0] * color_scalar, axial.r + vector[1] * color_scalar)

            tile = tiles.get(Axial(new_axial[0], new_axial[1]).to_string())
            if tile is None:
                continue

            if tile.piece is not None:
                if tile.piece.color != self.color:
                    possible_moves.append(tile)
                continue

            possible_moves.append(tile)

        for tile in possible_moves:  # Check for checkmates, etc. here
            legal_move = super().is_legal_move(tile)
            if legal_move:
                legal_moves.append(tile)

        return legal_moves

    def __deepcopy__(self, memodict=None, piece_copy=None):
        if memodict is None:
            memodict = {}

        piece_copy = Knight(copy(self.color), copy(self.current_position), self.board, self.board.piece_scale)

        return super().configure_copy(piece_copy=piece_copy)


class Bishop(Piece):
    def __init__(self, color: int, position: str, board, scale=1.0):
        super().__init__(color, "bishop", position, board, scale)

    def get_piece_moves(self, tiles: dict) -> list:
        legal_moves = []
        possible_moves = []
        axial = position_to_axial(self.current_position)

        movement_vectors = [
            (-2, 1),
            (-1, -1),
            (1, -2),
            (2, -1),
            (1, 1),
            (-1, 2)
        ]

        color_scalar = 1

        if self.color == 0:
            color_scalar = -1

        for vector in movement_vectors:
            i = 1
            while True:
                new_axial = (axial.q + vector[0] * color_scalar * i, axial.r + vector[1] * color_scalar * i)

                tile = tiles.get(Axial(new_axial[0], new_axial[1]).to_string())
                if tile is None:
                    break

                if tile.piece is not None:
                    if tile.piece.color != self.color:
                        possible_moves.append(tile)
                    break

                possible_moves.append(tile)
                i += 1

        for tile in possible_moves:  # Check for checkmates, etc. here
            legal_move = super().is_legal_move(tile)
            if legal_move:
                legal_moves.append(tile)

        return legal_moves

    def __deepcopy__(self, memodict=None, piece_copy=None):
        if memodict is None:
            memodict = {}

        piece_copy = Bishop(copy(self.color), copy(self.current_position), self.board, self.board.piece_scale)

        return super().configure_copy(piece_copy=piece_copy)


def create_default_pieces(color: int, board, scale=1.0) -> list[Piece]:
    pieces = [Queen(color, positions.get(str(color) + "queen"), board, scale),
              King(color, positions.get(str(color) + "king"), board, scale)]

    for position in positions.get(str(color) + "pawn"):
        pieces.append(Pawn(color, position, board, scale))

    for position in positions.get(str(color) + "rook"):
        pieces.append(Rook(color, position, board, scale))

    for position in positions.get(str(color) + "knight"):
        pieces.append(Knight(color, position, board, scale))

    for position in positions.get(str(color) + "bishop"):
        pieces.append(Bishop(color, position, board, scale))

    return pieces


def create_piece(color: int, piece: str, position: str, board, scale=1.0) -> Piece | None:
    match piece:
        case "queen":
            return Queen(color, position, board, scale)
        case "king":
            return King(color, position, board, scale)
        case "pawn":
            return Pawn(color, position, board, scale)
        case "rook":
            return Rook(color, position, board, scale)
        case "knight":
            return Knight(color, position, board, scale)
        case "bishop":
            return Bishop(color, position, board, scale)
        case _:
            return None
