from Deck import Deck

class Player():
    def __init__(self, id: str) -> None:
        self.id: str = id
        self.hand: Deck = Deck()

    def draw(self, deck: Deck) -> None:
        #Draw a Card from the current deck
        self.hand.add_to_top(deck.draw())

    def __str__(self) -> str:
        return self.id
