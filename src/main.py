import pygame
from pygame.locals import *
import os
import sys
from math import sqrt
import time

from piece import Piece
from utilities import draw_regular_polygon
from board import Board, Tile
from components import Button, Label, Dropdown
from settings import Settings
from axial import Axial, axial_from_string
from event_handler import EventHandler


def main_menu() -> None:
    """

    Main menu of the game

    :return: None
    """

    settings = Settings("settings.pkl")
    screen = pygame.display.set_mode(settings.dimensions)

    title_font_size = int(settings.dimensions[1] / 100) * 8
    button_font = pygame.font.Font(None, title_font_size // 2)
    title_font = pygame.font.Font(None, title_font_size)

    x = settings.dimensions[0] / 2 - 100
    y = settings.dimensions[1] / (5 + 1 / 3)
    text_width = 200

    buttons = [
        Button(x, y, text_width, 50, "Play Game"),
        Button(x, y + 125, text_width, 50, "Test Mode"),
        Button(x, y + 250, text_width, 50, "Settings"),
        Button(x, y + 375, text_width, 50, "Quit Game"),
    ]
    title = Label(x, 25, text_width, 50, "Hexagonal Chess")

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button.is_clicked(mouse_pos):
                        match button.text:
                            case "Quit Game":
                                running = False
                            case "Settings":
                                settings_changed = settings_menu(screen, settings)

                                if settings_changed:
                                    x = settings.dimensions[0] / 2 - 100
                                    y = settings.dimensions[1] / (5 + 1 / 3)

                                    for i, component in enumerate(buttons):
                                        component.rect.x = x
                                        component.rect.y = y + 125 * i

                                    title.rect.x = x

                            case "Play Game":
                                game_loop(settings)
                            case "Test Mode":
                                pass

        screen.fill(pygame.Color('grey'))

        for button in buttons:
            button.draw(screen, button_font)

        title.draw(screen, title_font, pygame.color.Color(38, 28, 55))

        pygame.display.flip()


def settings_menu(screen: pygame.surface.Surface, settings: Settings) -> bool:
    current_dimensions = settings.dimensions
    str_dimensions = str(current_dimensions[0]) + "x" + str(current_dimensions[1])

    dropdown = Dropdown(current_dimensions[0] / 2 - 50, 100, 200, 50, ["600x600", "700x700","800x800"])
    dropdown.select_option(str_dimensions)

    dropdown_label = Label(current_dimensions[0] / 2 - 200, 100, 100, 50, "Window Size")
    font = pygame.font.Font(None, int(current_dimensions[1] / 100) * 8 // 2)

    buttons = [
        Button(current_dimensions[0] / 2 + 25, current_dimensions[1] - 100, 200, 50,
                             "Save settings"),
        Button(current_dimensions[0] / 2 - 225, current_dimensions[1] - 100, 200, 50,
                               "Cancel changes")
    ]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if dropdown.rect.collidepoint(mouse_pos):
                    dropdown.toggle_dropdown()
                elif dropdown.is_open:
                    for i, option in enumerate(dropdown.options):
                        option_rect = pygame.Rect(dropdown.rect.x, dropdown.rect.y + (i + 1) * dropdown.rect.height,
                                                  dropdown.rect.width, dropdown.rect.height)
                        if option_rect.collidepoint(mouse_pos):
                            dropdown.select_option(option)

                for button in buttons:
                    if button.is_clicked(mouse_pos):
                        match button.text:
                            case "Save settings":
                                new_dimensions_str = dropdown.selected_option
                                new_dimensions = (int(new_dimensions_str[:3]), int(new_dimensions_str[4:]))

                                settings.set_window_dimensions(new_dimensions)
                                pygame.display.set_mode(new_dimensions)

                                settings.save_settings()
                                return True
                            case "Cancel changes":
                                return False


        screen.fill(pygame.Color("grey"))
        dropdown_label.draw(screen, font, pygame.Color(38, 28, 55))
        dropdown.draw(screen, font, pygame.Color(180, 180, 180), pygame.Color(38, 28, 55))

        for button in buttons:
            button.draw(screen, font)

        pygame.display.flip()


def game_loop(settings: Settings) -> None:
    """
    Main game loop

    :return: None
    """

    screen = pygame.display.set_mode(settings.dimensions)
    clock = pygame.time.Clock()

    #  Determining scale, x, and y for the board
    scale = settings.dimensions[0] * 0.0009375
    half_board_width = 50 * scale * 16 / 2
    board_x = settings.dimensions[0] / 2 - half_board_width
    board_y = (settings.dimensions[0] / 100 - 6) * 30 + 190

    board = Board(screen, settings, scale=scale, startX=board_x, startY=board_y)

    font = pygame.font.Font(None, 36)
    turn_label = Label(settings.dimensions[0] / 2 - 112, 0, 200, 50, "White's turn")

    mouse_button_down = EventHandler(MOUSEBUTTONDOWN, [])
    mouse_button_up = EventHandler(MOUSEBUTTONUP, [])

    board.add_event_handlers(mouse_button_up, mouse_button_down)

    board.start_game()



    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(pygame.Color('grey'))

        turn_label.draw(screen, font, pygame.Color('white'))

        board.update(events)

        if board.turn == 0:
            turn_label.set_text("Black's turn")
        else:
            turn_label.set_text("White's turn")

        pygame.display.flip()

        clock.tick(60)


def test():
    pass


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagonal Chess")

    main_menu()
    # test()

    pygame.quit()
    sys.exit()

'''
TODO
 main.py
  - Add settings menu. 
  
    - Screen size: Allow box only shape i.e. 600x600, 700x700, 800x800, 900x900. Figure out how the relationship between 
    board scale, piece scale, and screen size. 
    
    - Color of occupied tile and color of possible move tiles

  - Add normal mode and test mode in the main game loop. Normal mode is normal gameplay, while test mode doesn't have
    turns so the user can move any color piece.
    
    - Test mode should also have options for the user to create new pieces on the board wherever they want
      - Add text with letters signifying which piece. When corresponding letter is clicked, create that piece at the 
        cursor if it is a valid tile

 board.py
 utilities.py
 piece.py
'''