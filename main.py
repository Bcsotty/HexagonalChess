import pygame
from pygame.locals import *
import os
import sys
from math import sqrt
import time

from piece import Piece
from utilities import draw_regular_polygon
from board import Board, Tile


def game_loop() -> None:
    """
    Main game loop

    :return: None
    """

    screen = pygame.display.set_mode((800, 900))
    clock = pygame.time.Clock()

    board = Board(screen, scale=0.75)

    board.start_game()

    font = pygame.font.Font(None, 36)
    text = "White's turn"

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(pygame.Color('grey'))

        text_surface = font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (310, 780))

        # tile_test = Tile(pygame.color.Color("red"), "a6", (100, 250), 37.5)
        # tile_test.draw_tile(screen)

        turn = board.update(events)

        if turn == 0:
            text = "Black's turn"
        else:
            text = "White's turn"

        pygame.display.flip()

        clock.tick(60)


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagonal Chess")
    game_loop()


'''
TODO
 - Make the board tiles into sprites so the color can be edited to signify possible moves. Shade it red to make it a 
 possible move.
'''