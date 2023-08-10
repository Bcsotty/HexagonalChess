import pygame
from pygame.locals import *
import os
import sys
from math import sqrt

from piece import Piece
from utilities import draw_regular_polygon


def generate_board(surface, startX=100, startY=250, scale=1.0):
    colors = {
        0: pygame.Color(255, 206, 158),
        1: pygame.Color(232, 171, 111),
        2: pygame.Color(209, 139, 71)
    }

    i = j = 0
    size = 50 * scale
    width = size * 2
    height = sqrt(3) * size
    midY = startY - height / 2 * 5

    for i in range(11):

        rows = 6 + i if i < 6 else 16 - i

        for j in range(rows):
            x = startX + 3 / 4 * width * i
            if i < 6:
                y = startY - height / 2 * i + height * j
                color = colors.get((j + i) % 3)
            else:
                y = midY + height / 2 * (i - 5) + height * j
                color = colors.get((7 - i + j) % 3)

            draw_regular_polygon(surface, color, 6, size, (x, y))


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
        generate_board(screen, scale=0.75)
        sprites.draw(screen)
        pygame.display.flip()

        clock.tick(60)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagonal Chess")
    game_loop()
