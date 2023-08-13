import pygame
from utilities import get_piece_image, position_to_cartesian, position_to_rank_and_file, position_to_axial, \
    pixel_to_axial
from pygame.locals import *

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


class Piece(pygame.sprite.Sprite):
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
        self.rect.center = position_to_cartesian(position)
        self.dragging = False
        self.did_en_passant = False  # It is a joyous occasion when this is true
        self.board = board

    def update(self, tiles: dict):
        if self.dragging:
            self.rect.center = pygame.mouse.get_pos()

            for axial, tile in tiles.items():
                if pixel_to_axial(self.rect.center) == axial:
                    self.current_position = tile.position
                    break

    def handle_event(self, event: pygame.event.Event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.previous_position = self.current_position
                self.dragging = True
                return self

        elif event.type == MOUSEBUTTONUP:
            tiles = self.board.tiles

            if self.dragging:
                found_tile = False
                for axial, tile in tiles.items():
                    if (pixel_to_axial(self.rect.center) == axial and tile in self.board.highlighted_tiles and
                            tile.position != self.previous_position):
                        self.current_position = tile.position
                        self.rect.center = tile.cartesian_coordinates

                        if not tile.piece == self and tile.piece is not None:
                            self.board.remove_piece(tile.piece)

                        if self.did_en_passant:  # Hooray!
                            self.did_en_passant = False
                            additive = -1 if self.color == 0 else 1
                            dead_pawn_axial = (axial[0], axial[1] + additive)
                            self.board.remove_piece(tiles.get(dead_pawn_axial).piece)

                        tile.piece = self
                        found_tile = True

                        old_tile = tiles.get(position_to_axial(self.previous_position))
                        old_tile.piece = None

                        break

                if not found_tile:
                    self.current_position = self.previous_position
                    self.rect.center = position_to_cartesian(self.current_position)

                self.dragging = False
                return found_tile

        return None

    def get_piece_moves(self, tiles: dict):
        legal_moves = []
        possible_moves = []
        axial = position_to_axial(self.current_position)

        movement_vectors = {
            "pawn": [
                (-1, 0),  # Capture left
                (1, -1),  # Capture right
                (0, -1),  # Forward 1
                (0, -2),  # Forward 2 (Starting spot)
            ]
        }

        color_scalar = 1

        if self.color == 0:
            color_scalar = -1

        match self.name:
            case "pawn":
                start_locations = positions.get(str(self.color) + "pawn")

                for vector in movement_vectors.get("pawn"):
                    if self.current_position not in start_locations:
                        if vector[1] == -2:
                            continue

                    new_axial = (axial[0] + vector[0] * color_scalar, axial[1] + vector[1] * color_scalar)

                    tile = tiles.get(new_axial)
                    if tile is None:
                        continue

                    if not (vector[0] == 0):
                        piece_moved = self.board.last_piece_moved

                        if piece_moved is not None:
                            if piece_moved.name == "pawn":
                                if piece_moved.previous_position in positions.get(str(piece_moved.color) + "pawn"):
                                    piece_axial = position_to_axial(piece_moved.current_position)

                                    if (new_axial[0] == piece_axial[0]) and (
                                            new_axial[1] + color_scalar == piece_axial[1]):

                                        self.did_en_passant = True  # This is where a steam achievement is added
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
            legal_moves.append(tile)

        return legal_moves


def create_pieces(color: int, board, scale=1.0) -> list[Piece]:
    pieces = [Piece(color, "queen", positions.get(str(color) + "queen"), board, scale),
              Piece(color, "king", positions.get(str(color) + "king"), board, scale)]

    for position in positions.get(str(color) + "pawn"):
        pieces.append(Piece(color, "pawn", position, board, scale))

    for position in positions.get(str(color) + "rook"):
        pieces.append(Piece(color, "rook", position, board, scale))

    for position in positions.get(str(color) + "knight"):
        pieces.append(Piece(color, "knight", position, board, scale))

    for position in positions.get(str(color) + "bishop"):
        pieces.append(Piece(color, "bishop", position, board, scale))

    return pieces
