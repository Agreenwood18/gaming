from Deck import Deck
from util import get_int_response, prompt_yes_or_no

class Player():
    def __init__(self, id):
        self.id = id
        self.hand: Deck = Deck()
        # self.bank: Bank = Bank() # MOVE TODO

    def draw(self, deck):
        #Draw a Card from the current deck
        self.hand.add_to_top(deck.draw())

    def __str__(self):
        #Display your hand
        return f"({self.id}) has {len(self.hand)} cards: {str(self.hand)}" 

class BlackJackPlayer(Player):
    def __init__(self, id):
        super().__init__(id)

    def can_hit(self):
        return 21 > sum(int(c) if int(c) != -1 else 1 for c in self.hand)

    def ace_descision(self):
        #User chooses what value they want the ace to be
        a_point = 0
        while True:
            a_point = get_int_response("Do you want your Ace to be worth 11 or 1? ")
            if a_point == 11 or a_point == 1:
                break
        return a_point

    def point_checker(self):
        #checks players points
        points = 0
        for card in self.hand:
            card_num = int(card)
            if card_num == -1:
                card_num = self.ace_descision()
            
            points += card_num

        return points

    def hit(self, deck):
        if prompt_yes_or_no("Hit or stay?"):
            self.draw(deck)
            return True

        return False

class BlackJackDealer(BlackJackPlayer):
    def __init__(self):
        super().__init__("Dealer")
        self.has_decided_on_11 = False
    
    def point_checker(self):
        #check dealer points
        self.has_decided_on_11 = False
        points = super().point_checker()

        return points     

    def ace_descision(self):
        #ace decision for dealer
        """
        2+ cards in hand (1 ace) ace = 11 if other cards sum less than or equal to 10

        2 cards in hand (2 aces) ace a = 1 ace b 11

        3+ cards in hand (2 aces) ace a =1 ace b =11 only if sum of other cards is less than or equal to 9

        3 cards in hand (3 aces) ace a = 1 ace b =1 ace c = 11

        4+ cards in hand (3 aces) ace a = 1 ace b =1 ace c =11 only if sum of other cards is less than or equal to 8

        4 cards in hand (4 aces) ace a =1 ace b =1 ace c=1 ace d =11

        5+ cards in hand (4 aces) ace a =1 ace b =1 ace c=1 ace d =11 only if sum of other cards is less than or equal to 7

        /////////////else all ace equal 1, applies to all//////////
        """
        ace_num = 0
        total_without_aces = 0
        if self.has_decided_on_11:
            ace_num = 1
        else:
            for card in self.hand:
                card_num = int(card)
                if card_num == -1:
                    ace_num += 1
                else:
                    total_without_aces += card_num

            match ace_num:
                case 1:
                    if total_without_aces <= 10:
                        ace_num = 11
                        self.has_decided_on_11 = True
                    else:
                        ace_num = 1
                case 2:
                    if total_without_aces <= 9:
                        ace_num = 11
                        self.has_decided_on_11 = True
                    else:
                        ace_num = 1
                case 3:
                    if total_without_aces <= 8:
                        ace_num = 11
                        self.has_decided_on_11 = True
                    else:
                        ace_num = 1
                case 4:
                    if total_without_aces <= 7:
                        ace_num = 11
                        self.has_decided_on_11 = True
                    else:
                        ace_num = 1 
            
        return ace_num

    def hit(self, deck):
        current_points = self.point_checker()
        
        #did_hit = False
        while current_points < 17:
            self.draw(deck)
            current_points = self.point_checker()
        
        return current_points#, did_hit

    
