import socket
import time
import threading
import pickle
import select


class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, address, port) -> bool:
        try:
            self.socket.connect((address, port))
            self.socket.setblocking(False)
            return True
        except ConnectionRefusedError:
            return False

    def send_str(self, data: str):
        self.socket.sendall(data.encode())

    def send_list(self, data: list):
        data_string = pickle.dumps(data)
        self.socket.sendall(data_string)

    def recv_str(self) -> str:
        ready = select.select([self.socket], [], [], 5)
        if ready[0]:
            data = self.socket.recv(4096)
            return data.decode('utf-8')

    def recv_list(self) -> list:
        ready = select.select([self.socket], [], [], 5)
        if ready[0]:
            data = self.socket.recv(4096)
            return pickle.loads(data)

    def __del__(self):
        self.socket.close()
