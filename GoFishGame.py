from MultiDeckPlayer import MultiDeckPlayer
from Game import Game
from UIController import UIController


class GoFishGame(Game):
    def __init__(self, player_ids, UI_controller: UIController) -> None:
        super().__init__("Go Fish", UI_controller)
        self.players: list[MultiDeckPlayer] = []

    def start(self, _player_ids: list[str]) -> None:
        super().start(_player_ids)
