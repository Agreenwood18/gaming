from Deck import Deck
from Player import Player


class MultiDeckPlayer(Player):
    def __init__(self, id: str, num_decks=2) -> None:
        if num_decks < 2:
            raise ValueError("MultiDeckPlayer must have more than 2 decks")

        super().__init__(id)
        self.decks: list[Deck] = [Deck() * (num_decks - 1)]

    @property
    def discard(self):
        return self.decks[0]
