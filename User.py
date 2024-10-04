class User:
    def __init__(self, socket, addr, player_id=None) -> None:
        self.player_id: str | None = player_id
        self.socket = socket
        self.addr = addr

    def start_using_player(self, unique_name: str) -> None:
        self.player_id = unique_name
