import socket
import time


def main():
    host = '127.0.0.1'
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print("Connected to server")

    start_time = time.time()
    while time.time() - start_time < 10:
        time.sleep(1)

    client_socket.close()


if __name__ == "__main__":
    main()
