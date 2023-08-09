import pygame
from pygame.locals import *
import os
import sys

from piece import Piece


def game_loop() -> None:
    """
    Main game loop

    :return: None
    """

    screen = pygame.display.set_mode((808, 896))
    clock = pygame.time.Clock()

    w_rook = Piece(1, "rook")
    b_pawn = Piece(0, "pawn", 100, 100)

    pieces = [w_rook, b_pawn]

    sprites = pygame.sprite.Group(w_rook, b_pawn)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            for piece in pieces:
                piece.handle_event(event)

        sprites.update()

        screen.fill(pygame.Color('grey'))
        sprites.draw(screen)
        pygame.display.flip()

        clock.tick(60)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagonal Chess")
    game_loop()
