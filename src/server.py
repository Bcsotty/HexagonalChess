import socket
import threading

def handle_client(client_socket: socket.SocketType, client_number: int) -> None:
    print(f"Client {client_number} connected")

    client_socket.close()
    print(f"Client {client_number} disconnected")


def main() -> None:
    host = '127.0.0.1'
    port = 12345
    clients = []

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(2)

    print("Server is listening for clients...")

    for client_number in range(1, 3):
        client_socket, client_address = server_socket.accept()
        print(f"Client {client_number} connected from {client_address}")
        clients.append((client_socket, client_number))

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_number))
        client_thread.start()

    for client_thread in threading.enumerate():
        if client_thread != threading.current_thread():
            client_thread.join()

    server_socket.close()


if __name__ == '__main__':
    main()
