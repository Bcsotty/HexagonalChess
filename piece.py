import pygame
from utilities import get_piece_image
from pygame.locals import *


class Piece(pygame.sprite.Sprite):
    """

    Piece sprite

    """
    def __init__(self, color: int, piece: str, x=0, y=0):
        """

        :param color: Color of the piece. 0 for black, 1 for white
        :param piece: The piece name
        :param x: x-Position to be placed at
        :param y: y-Position to be placed at
        """
        super().__init__()
        self.image = get_piece_image(color, piece)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.dragging = False

    def update(self):
        if self.dragging:
            self.rect.center = pygame.mouse.get_pos()

    def handle_event(self, event: pygame.event.Event):
        if event.type == MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == MOUSEBUTTONUP:
            self.dragging = False
