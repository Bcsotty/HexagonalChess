import pygame
from pygame.locals import *
import os
import sys
from math import sqrt
import time

from piece import Piece, create_piece
from utilities import draw_regular_polygon, clamp
from board import Board, Tile
from components import Button, Label, Dropdown, Slider, RGBPicker
from settings import Settings
from axial import Axial, axial_from_string, pixel_to_axial
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
                                test_mode(settings)

        screen.fill(pygame.Color('grey'))

        for button in buttons:
            button.draw(screen, button_font, settings.text_color)

        title.draw(screen, title_font, settings.text_color)

        pygame.display.flip()


def settings_menu(screen: pygame.surface.Surface, settings: Settings) -> bool:
    current_dimensions = settings.dimensions
    str_dimensions = str(current_dimensions[0]) + "x" + str(current_dimensions[1])

    dropdown = Dropdown(current_dimensions[0] / 2 - 50, 0, 200, 50, ["600x600", "700x700","800x800"])
    dropdown.select_option(str_dimensions)

    dropdown_label = Label(current_dimensions[0] / 2 - 200, 0, 100, 50, "Window Size")
    font = pygame.font.Font(None, int(current_dimensions[1] / 100) * 8 // 2)

    highlight_color_label = Label(current_dimensions[0] / 2 - 116, 175,
                        200, 100, "Tile highlight settings (RGB, from -255 to 255)")
    highlight_rgb_picker = RGBPicker(current_dimensions[0] / 2 - 150, 250, 255, 50, settings.highlight,
                                     -255)

    text_color_label = Label(current_dimensions[0] / 2 - 150, 310, 200, 100, "Text Color")
    text_rgb_picker = RGBPicker(current_dimensions[0] / 2 - 150, 385, 255, 50, settings.text_color)

    colors = {
        0: pygame.Color(255, 206, 158),
        1: pygame.Color(232, 171, 111),
        2: pygame.Color(209, 139, 71)
    }

    sample_tiles = []

    size = 37.5
    tile_width = size * 2
    tile_height = sqrt(3) * size

    for i in range(4):
        if i < 2:
            x = current_dimensions[0] / 2 - 250 + 3 / 4 * tile_width * 0
        else:
            x = current_dimensions[0] / 2 - 250 + 3 / 4 * tile_width * 1

        y = 375 + tile_height * i if i < 2 else 375 + tile_height * (i - 2) - tile_height / 2

        sample_tiles.append(Tile(colors.get(i % 3), str(i), (x, y), size))

    buttons = [
        Button(current_dimensions[0] / 2 + 25, current_dimensions[1] - 100, 200, 50,
                             "Save settings"),
        Button(current_dimensions[0] / 2 - 225, current_dimensions[1] - 100, 200, 50,
                               "Cancel changes")
    ]

    occupied_tile_sample = sample_tiles[-1]
    occupied_color = (clamp(100, occupied_tile_sample.color.r, 255),
                     clamp(-60, occupied_tile_sample.color.g, 255),
                     clamp(-60, occupied_tile_sample.color.b, 255))
    occupied_tile_sample.apply_filter(pygame.Color(occupied_color[0], occupied_color[1], occupied_color[2]))

    dragging_slider = None

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

                                highlight_rgb_picker.update_color()
                                new_highlight = highlight_rgb_picker.color
                                text_rgb_picker.update_color()
                                new_text_color = text_rgb_picker.color

                                settings.highlight = new_highlight
                                settings.dimensions = new_dimensions
                                settings.text_color = new_text_color
                                pygame.display.set_mode(new_dimensions)

                                settings.save_settings()
                                return True
                            case "Cancel changes":
                                return False

                for slider in highlight_rgb_picker.sliders + text_rgb_picker.sliders:
                    if slider.knob_rect.collidepoint(mouse_pos):
                        dragging_slider = slider
                        slider.update_value(mouse_pos[0])

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                dragging_slider = None
            elif event.type == MOUSEMOTION and dragging_slider:
                mouse_pos = pygame.mouse.get_pos()
                dragging_slider.update_value(mouse_pos[0])


        screen.fill(pygame.Color("grey"))
        text_rgb_picker.update_color()
        dropdown_label.draw(screen, font, pygame.Color(text_rgb_picker.color))
        dropdown.draw(screen, font, pygame.Color(180, 180, 180), pygame.Color(text_rgb_picker.color))

        for button in buttons:
            button.draw(screen, font, pygame.Color(text_rgb_picker.color))

        highlight_color_label.draw(screen, font, pygame.Color(text_rgb_picker.color))
        highlight_rgb_picker.draw(screen, font, pygame.Color('grey'), pygame.Color('white'))
        text_color_label.draw(screen, font, pygame.Color(text_rgb_picker.color))
        text_rgb_picker.draw(screen, font, pygame.Color('grey'), pygame.Color('white'))

        for tile in sample_tiles:
            tile.draw_tile(screen)

            if tile == sample_tiles[-1]:
                break

            highlight_rgb_picker.update_color()
            highlight = highlight_rgb_picker.color
            new_color = (clamp(tile.color.r, highlight[0], 255),
                         clamp(tile.color.g, highlight[1], 255),
                         clamp(tile.color.b, highlight[2], 255))
            tile.apply_filter(pygame.Color(new_color[0], new_color[1], new_color[2]))

        pygame.display.flip()


def game_loop(settings: Settings) -> None:
    """
    Main game loop

    :return: None
    """

    screen = pygame.display.set_mode(settings.dimensions)
    clock = pygame.time.Clock()

    board = Board(screen, settings)

    font = pygame.font.Font(None, 36)
    turn_label = Label(settings.dimensions[0] / 2 - 112, 0, 200, 50, "White's turn")

    promotion_labels = [
        Label(settings.dimensions[0] * 3 / 4 - 100, 0, 200, 50, "Choose a piece:"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 25, 200, 50, "q - Queen"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 50, 200, 50, "n - Knight"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 75, 200, 50, "r - Rook"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 100, 200, 50, "b - Bishop")
    ]

    board.start_game()
    sample_state = ['06050606', '07070706', '06060706', '08070806', '07060806', '09070906', '08060906', '10071006',
                    '09061006', '09081106', '100611061']
    # board.load_state(sample_state)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                print(board.state)
                pygame.quit()
                sys.exit()

        screen.fill(pygame.Color('grey'))

        turn_label.draw(screen, font, settings.text_color)

        if board.promotion_flag:
            for label in promotion_labels:
                label.draw(screen, font, settings.text_color)

        board.update(events)

        if board.turn == 0:
            turn_label.set_text("Black's turn")
        else:
            turn_label.set_text("White's turn")

        if board.game_over:
            # Replace bool with whether we win according to the last piece played color being ours or enemy
            game_over_screen(True, settings)
            break

        pygame.display.flip()

        clock.tick(60)


def test_mode(settings: Settings) -> None:
    screen = pygame.display.set_mode(settings.dimensions)

    board = Board(screen, settings, True)

    board.generate_blank_board()

    board.add_event_handlers()

    promotion_labels = [
        Label(settings.dimensions[0] * 3 / 4 - 100, 0, 200, 50, "Choose a piece:"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 25, 200, 50, "q - Queen"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 50, 200, 50, "n - Knight"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 75, 200, 50, "r - Rook"),
        Label(settings.dimensions[0] * 3 / 4 - 75, 100, 200, 50, "b - Bishop")
    ]
    font = pygame.font.Font(None, 36)

    running = True
    key_last_pressed = 0.
    while running:
        events = pygame.event.get()
        keys = pygame.key.get_pressed()

        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        piece_color = 1
        if keys[K_LSHIFT] or keys[K_RSHIFT]:
            piece_color = 0

        if time.time() - key_last_pressed > 0.25:
            tile = board.tiles.get(pixel_to_axial(board, pygame.mouse.get_pos()).to_string())
            if tile is not None:
                if tile.piece is None:
                    if keys[K_p]:
                        piece = create_piece(piece_color, "pawn", tile.position, board, board.piece_scale)
                        board.add_piece(piece)
                        key_last_pressed = time.time()
                    elif keys[K_b]:
                        piece = create_piece(piece_color, "bishop", tile.position, board, board.piece_scale)
                        board.add_piece(piece)
                        key_last_pressed = time.time()
                    elif keys[K_n]:
                        piece = create_piece(piece_color, "knight", tile.position, board, board.piece_scale)
                        board.add_piece(piece)
                        key_last_pressed = time.time()
                    elif keys[K_r]:
                        piece = create_piece(piece_color, "rook", tile.position, board, board.piece_scale)
                        board.add_piece(piece)
                        key_last_pressed = time.time()
                    elif keys[K_q]:
                        piece = create_piece(piece_color, "queen", tile.position, board, board.piece_scale)
                        board.add_piece(piece)
                        key_last_pressed = time.time()
                    elif keys[K_k]:
                        piece = create_piece(piece_color, "king", tile.position, board, board.piece_scale)
                        board.add_piece(piece)
                        key_last_pressed = time.time()
                if keys[K_BACKSPACE]:
                    mouse_axial = pixel_to_axial(board, pygame.mouse.get_pos())
                    hovered_piece = board.tiles.get(mouse_axial.to_string()).piece
                    if hovered_piece is not None:
                        board.remove_piece(hovered_piece)
                    key_last_pressed = time.time()

        screen.fill(pygame.Color('grey'))

        if board.promotion_flag:
            for label in promotion_labels:
                label.draw(screen, font, settings.text_color)

        if board.game_over:
            # Replace bool with whether we win according to the last piece played color being ours or enemy
            game_over_screen(True, settings)
            break

        board.update(events)
        pygame.display.flip()


def game_over_screen(is_winner: bool, settings: Settings):
    screen = pygame.display.set_mode(settings.dimensions)

    if is_winner:
        text = "You win!"
    else:
        text = "You lost..."

    font = pygame.font.Font(None, 36)

    end_state = Label(settings.dimensions[0] / 2 - 50, 120, 100, 100, text)
    main_menu_button = Button(settings.dimensions[0] / 2 - 100, settings.dimensions[1] - 200, 200, 50,
                              "Main Menu")

    running = True
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                if main_menu_button.is_clicked(mouse_pos):
                    running = False

        screen.fill(pygame.Color('grey'))

        end_state.draw(screen, font, settings.text_color)
        main_menu_button.draw(screen, font, settings.text_color)

        pygame.display.flip()


if __name__ == '__main__':
    pygame.init()
    pygame.display.set_caption("Hexagonal Chess")

    main_menu()

    pygame.quit()
    sys.exit()

'''
TODO
 - Add some form of notation to the board with save and load methods for placing the the pieces.
 
 - Add server and client.
   - Server stores client information, the IP gets mapped to the users name in the settings. If left as default, then
   auto-assign the name of the IP. The server would tell each client what color it is, and when the client sends their
   board state (the current state in the notation) the server will save the state to logs, update the turn, then send 
   the board state to the other client. The server should then check if the board state was terminal, and if so it will
   close the connection to the clients.
    - Optional features when closing connection could be sending the players match history W-L
    
   - Client will play the game. It will have the option to play local which is the default game we have made, then a 
   second button will be on the main menu for multiplayer. Once the client clicks multiplayer, it will have an input for
   an IP and a port, and a connect button. Once the user enters the IP and port, if it fails to connect it will display
   a red label saying connection failed. If it does connect, it will instead get the players color from the server and 
   orient the board accordingly. When its the players turn they can play their move and it will get sent to the server.
   Once their turn is done, the client will wait for the server to respond with the next move and will display the other
   players turn.
 
 - Add which color you are to the game screen (Low priority since it makes no difference until multiplayer is implemented)
 - Add the ability to see from black perspective (Low priority since moving works as is)
 - Refactor the code (at the end)
'''