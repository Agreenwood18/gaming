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
    
    #needs to be implemented
    def remove_specific_card(self, card:Card):
        pass

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

    def num_only(self):
        num_cards: list[str] = []
        for card in self.cards:
            if type(card.val)==int:
                num_cards.append(str(card.val))
            else:
                num_cards.append(card.val)


        print(num_cards)
        return num_cards
    
    #used in go fish
    def pair_search(self) -> list[Card] :
        numcard = self.num_only()
        pairs: list[Card] = []
        for i in range(len(numcard)):
            for j in range(len(numcard)):
                if i != j:
                    if numcard[i]==numcard[j]:
                        if pairs.count(self.cards[i]) == 0 and pairs.count(self.cards[j]) == 0:
                            pairs.append(self.cards[i])
                            pairs.append(self.cards[j])

        return pairs       
                
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
