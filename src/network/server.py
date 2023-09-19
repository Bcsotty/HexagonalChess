import socket
import threading
import sys
import pickle
from sqlite3 import connect
import pygame

from src.network.database import Database
from src.chess.board import Board
from src.tools.settings import Settings


white_turn = threading.Event()
white_turn.set()
state = None
clients = []


def client_thread(client_socket: socket.SocketType, client_number: int, client_name: str, board: Board, database: Database) -> None:
    global state

    while True:
        if (white_turn.is_set() and client_number == 1) or (not white_turn.is_set() and client_number == 2):
            new_state = client_socket.recv(4096)
            new_state_array = pickle.loads(new_state)

            print(f'Received new state from client: {new_state_array}')
            if white_turn.is_set():
                white_turn.clear()
            else:
                white_turn.set()
            state = new_state_array
        else:
            if state is not None:
                state_bytes = pickle.dumps(state)
                client_socket.sendall(state_bytes)

                board.reset_board()
                board.load_state(state)
                if board.game_over:
                    separator = ','
                    state_string = separator.join(state)
                    opponent_name = clients[0][2] if clients[0][2] != client_name else clients[1][2]
                    winner = client_name if ((board.last_piece_moved.color == 0 and client_number == 2) or
                                             (board.last_piece_moved.color == 1 and client_number == 1)) else opponent_name
                    database.add_game(client_name, opponent_name, winner, state_string)
                    break

                state = None
    client_socket.close()


def main() -> None:
    global clients

    host = '127.0.0.1'
    port = 12345
    if len(sys.argv) > 1:
        new_port = sys.argv[1]
        try:
            new_port = int(new_port)
            port = new_port
        except ValueError:
            pass

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)

    database = Database()
    settings = Settings("settings.pkl")
    pygame.display.init()
    board = Board(pygame.Surface((0, 0)), settings)

    try:
        while True:
            # board.reset_board()
            print("Server is listening for clients...")

            for client_number in range(1, 3):
                client_socket, client_address = server_socket.accept()
                print(f"Client {client_number} connected from {client_address}. Waiting for clients name...")

                name = client_socket.recv(1024).decode('utf-8')
                print(f"Clients name is {name}")
                player = database.get_player_from_name(name)
                if player is None:
                    print("Player not in database. Adding player")
                    database.add_player(name, client_address[0])

                color = '1' if client_number == 1 else '0'
                client_socket.sendall(color.encode())

                clients.append((client_socket, client_number, name))

                client = threading.Thread(target=client_thread, args=(client_socket, client_number, name, board, database))
                client.start()

            for thread in threading.enumerate():
                if thread != threading.current_thread():
                    thread.join()

            clients = []
    except KeyboardInterrupt:
        pass

    server_socket.close()
    database.close_database()


if __name__ == '__main__':
    main()
    pygame.quit()
