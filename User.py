import socket


class User:
    def __init__(self, sock, addr, player_id=None) -> None:
        self.player_id: str | None = player_id
        self.socket: socket.socket = sock
        self.addr = addr

    def start_using_player(self, unique_name: str) -> None:
        self.player_id = unique_name

    def send_message(self, msg: str):
        self.socket.sendall(msg.encode())

    def receive_message(self):
        try:
            return self.socket.recv(1024).decode().strip()
        except socket.error as e:
            print(f"Error receiving message from {self.addr}: {e}")
            return None
