import socket
import threading
from GameManager import GameManager
from User import User


class UserRouter:
    def __init__(self, host='127.0.0.1', port=12345) -> None:
        self.__is_running: bool = False
        self.lobbies: dict[str, GameManager] = {}
        self.host: str = host
        self.port: int = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.__thread_lock: threading.Lock = threading.Lock() # now with thread safety! maybe? TODO: unit test it my man

    
    def start_thread(self) -> None:
        if self.__is_running:
            raise ValueError("this thread is already running...")

        self.__is_running = True
        listener_thread = threading.Thread(target=self.listen_for_connections)
        listener_thread.start()

    def stop_thread(self) -> None:
        with self.__thread_lock:
            self.__is_running = False

    def listen_for_connections(self) -> None:
        while self.__is_running:
            user_socket, addr = self.server_socket.accept()
            lobby = self.__get_or_create_lobby()
            lobby.add_user(User(user_socket, addr))
            
            # user_thread = threading.Thread(target=self._handle_user_thread, args=(user_socket,))
            # user_thread.start()

    def __get_or_create_lobby(self) -> GameManager:
        with self.__thread_lock:
            lobby_id = 99999 # TODO: make random and meaningful for multiple lobbies
            if lobby_id not in self.lobbies:
                new_lobby = GameManager()
                self.lobbies[lobby_id] = new_lobby
                lobby_thread = threading.Thread(target=self.__handle_lobby_thread, args=lobby_id)
                lobby_thread.start()
            return self.lobbies[lobby_id]
        
    def __handle_lobby_thread(self, lobby_id) -> None: # TODO: this will be in lobby...
        lobby: GameManager = self.lobbies[lobby_id]
        try:
            while True:
                lobby.wait_in_lobby() # maybe leave or hop back into a new game? idk
                lobby.game_selector()
                lobby.start_game() # game finishes and you're kicked back out to the lobby
        finally:
            pass
            # TODO: all of em: user_socket.close()
