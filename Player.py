from Deck import Deck

class Player():
    def __init__(self, id) -> None:
        self.id = id
        self.hand: Deck = Deck()
        # self.bank: Bank = Bank() # MOVE TODO

    def draw(self, deck: Deck) -> None:
        #Draw a Card from the current deck
        self.hand.add_to_top(deck.draw())

    def __str__(self) -> str:
        #Display your hand
        return f"({self.id}) has {len(self.hand)} cards: {str(self.hand)}" 
