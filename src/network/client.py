import socket
import time
import threading


def main():
    host = '127.0.0.1'
    port = 12345

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    print("Connected to server. Sending name")

    client_socket.sendall(b'Jeff2')
    start_time = time.time()
    while time.time() - start_time < 10:
        time.sleep(1)

    client_socket.close()

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, address, port) -> bool:
        try:
            self.socket.connect((address, port))
            return True
        except TimeoutError:
            return False

    def send_data(self, data):
        self.socket.sendall(data)
