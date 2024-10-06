import socket
import threading


from LobbyManager import LobbyManager
from User import User
from util import SingletonClass


class UserRouter(SingletonClass):
    def __init__(self, host='0.0.0.0', port=8080) -> None:
        self.host: str = host
        self.port: int = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__lobby_manager = LobbyManager()
        self.__is_running: bool = False

    def start_listening(self) -> None:
        if self.__is_running:
            raise ValueError("this thread is already running...")

        self.__is_running = True
        listener_thread = threading.Thread(target=self.__listen_for_connections)
        listener_thread.start()

    def stop_thread(self) -> None:
        self.__is_running = False

    def __listen_for_connections(self) -> None:
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        def get_local_ip():
            # Create a temporary socket to connect to an external IP
            # (doesn't actually send any data, just checks routing)
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Connect to an external server (e.g., Google's DNS server) without sending data
            try:
                temp_socket.connect(("8.8.8.8", 80))
                local_ip = temp_socket.getsockname()[0]
            finally:
                temp_socket.close()
            
            return local_ip

        # Get the actual local IP address
        print(f"My IP Address: {get_local_ip()}")

        # print(f"server starting listening on {self.host} {self.port}")
        while self.__is_running:
            user_socket, addr = self.server_socket.accept()
            print(f"user {user_socket} {addr} connected. Passing to lobby manager")
            new_user = User(user_socket, addr, "NO_PLAYER")
            self.__lobby_manager.manage_user(new_user)
            