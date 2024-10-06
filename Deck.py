from typing import Iterator
from Card import Card
import random


class Deck:
    ## NOTE Top of the deck is the last card in the list

    def __init__(self, val=[], suits=[], val_map={}) -> None:
        self.val_mapping = val_map
        self.cards: list[Card] = []
        self.__build(val, suits)

    def get_top(self) -> Card:
        return self.cards[-1]

    def add_to_top(self, card: Card) -> None:
        self.cards.append(card)

    def add_to_bottom(self, card: Card) -> None:
        self.cards.insert(0, card)

    def clear(self) -> None:
        # destroy all cards in your deck
        self.cards = []
    
    def draw(self) -> Card:
        #removes the drawn card from the deck
        return self.cards.pop()

    def shuffle(self) -> None:
        #shuffle the deck
        random.shuffle(self.cards)
        # i = len(self.cards)
        # for x in range(i):
        #     current = self.cards[x]
        #     self.cards.pop(x)
        #     self.cards.insert(random.randrange(0,51),current)

    def __build(self, val, suits) -> None: 
        #This is base code for making a deck
        for rank in val: 
            for suit in suits:
                int_val = None
                if rank in self.val_mapping:
                    int_val = self.val_mapping[rank]
                c1= Card(rank, suit, int_val=int_val)
                self.cards.append(c1)

    def __getitem__(self, key):
        return self.cards[key]

    def __str__(self) -> str:
        #prints the current deck        
        return ", ".join([str(card) for card in self.cards])

    def __iter__(self):
        return reversed(self.cards).__iter__()
    
    def __len__(self) -> int:
        return self.cards.__len__()
    
    def __int__(self):
        return sum(self.cards)
    
    def __add__(self, other):
        return self.__int__() + other.__int__()

    def __radd__(self, other):
        return self.__add__(other)
