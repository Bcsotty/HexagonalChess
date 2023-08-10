import pygame
from pygame.locals import *
import os
import sys
from math import sqrt

from piece import Piece
from utilities import draw_regular_polygon
from board import Board


def game_loop() -> None:
    """
    Main game loop

    :return: None
    """

    screen = pygame.display.set_mode((808, 896))
    clock = pygame.time.Clock()

    board = Board(screen, scale=0.75)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                print(event.pos)

        screen.fill(pygame.Color('grey'))
        board.update(pygame.event.get())
        pygame.display.flip()

        clock.tick(60)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagonal Chess")
    game_loop()
