from typing import override
from Player import Player
from util import get_int_response, prompt_yes_or_no


class BlackJackPlayer(Player):
    def __init__(self, id) -> None:
        super().__init__(id)

    def can_hit(self) -> bool:
        return 21 > sum(int(c) if int(c) != -1 else 1 for c in self.hand)

    def ace_descision(self) -> int:
        #User chooses what value they want the ace to be
        a_point = 0
        while True:
            a_point = get_int_response("Do you want your Ace to be worth 11 or 1? ")
            if a_point == 11 or a_point == 1:
                break
        return a_point

    def get_score(self) -> int:
        def best(a: int, b: int):
            ## return the "best" score, which is the largest sum <= 21 (or the smaller total > 21)
            return max(filter(lambda c: c <= 21, [a, b]), default=min(a, b))

        def recurse_helper(card_i, curr_count) -> int:
            # if curr_count > 21:
            #     return 0
            if card_i >= len(self.hand):
                return curr_count
            
            card = self.hand[card_i]
            card_num = int(card)
            if card_num == -1:
                return best(recurse_helper(card_i + 1, curr_count + 1), recurse_helper(card_i + 1, curr_count + 11))
            else:
                return recurse_helper(card_i + 1, curr_count + card_num)

        return recurse_helper(0, 0)

    def hit(self, deck) -> bool:
        if prompt_yes_or_no("Hit or stay?"):
            self.draw(deck)
            return True

        return False

class BlackJackDealer(BlackJackPlayer):
    def __init__(self) -> None:
        super().__init__("Dealer")

    @override
    def hit(self, deck) -> int:
        current_points = self.get_score()
        
        while current_points < 17:
            self.draw(deck)
            current_points = self.get_score()
        
        return current_points
