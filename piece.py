import pygame
from utilities import get_piece_image, position_to_cartesian
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

    def __init__(self, color: int, piece: str, position: str, scale=1.0):
        """
        :param color: Color of the piece. 0 for black, 1 for white
        :param piece: The piece name
        :param position: The rank and file to be placed at. (a7, f2, etc.)
        """

        super().__init__()

        self.image = get_piece_image(color, piece, scale)
        self.name = piece
        self.color = color
        self.current_position = self.previous_position = position
        self.rect = self.image.get_rect()
        self.rect.center = position_to_cartesian(position)
        self.dragging = False

    def update(self, tiles: dict):
        if self.dragging:
            self.rect.center = pygame.mouse.get_pos()

            for tile in tiles.values():
                if (tile.bbox.topleft[0] <= self.rect.centerx <= tile.bbox.bottomright[0] and tile.bbox.topleft[1] <=
                        self.rect.centery <= tile.bbox.bottomright[1]):

                    self.current_position = tile.position
                    break

    def handle_event(self, event: pygame.event.Event, tiles: dict):
        if event.type == MOUSEBUTTONDOWN:
            self.previous_position = self.current_position
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                return self

        elif event.type == MOUSEBUTTONUP:
            if self.dragging:
                found_tile = False
                for tile in tiles.values():
                    if ((tile.bbox.topleft[0] <= self.rect.centerx <= tile.bbox.bottomright[0]) and
                            (tile.bbox.topleft[1] <= self.rect.centery <= tile.bbox.bottomright[1])):

                        self.current_position = tile.position
                        self.rect.center = tile.cartesian_coordinates
                        found_tile = True
                        break

                if not found_tile:
                    self.current_position = self.previous_position
                    self.rect.center = position_to_cartesian(self.current_position)

            self.dragging = False

        return None

    def get_piece_moves(self, tiles):
        match self.name:
            case "pawn":
                start_locations = positions.get(str(self.color) + "pawn")
                if self.current_position in start_locations:
                    pass  # TODO possibly switch to coordinate grid to make moves easier?


def create_pieces(color: int, scale=1.0) -> list[Piece]:
    pieces = [Piece(color, "queen", positions.get(str(color) + "queen"), scale),
              Piece(color, "king", positions.get(str(color) + "king"), scale)]

    for position in positions.get(str(color) + "pawn"):
        pieces.append(Piece(color, "pawn", position, scale))

    for position in positions.get(str(color) + "rook"):
        pieces.append(Piece(color, "rook", position, scale))

    for position in positions.get(str(color) + "knight"):
        pieces.append(Piece(color, "knight", position, scale))

    for position in positions.get(str(color) + "bishop"):
        pieces.append(Piece(color, "bishop", position, scale))

    return pieces
