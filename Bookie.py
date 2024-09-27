from util import get_int_response

class Bookie():
    def __init__(self):
        # {player_id: [balance, current_bet]}
        self.player_dict = dict()

        # self.current_bet = 0
        # self.balance = 0
        self.minBal = 100
        self.maxBal = 300
    
    def lost_bet(self, id):
        bal, cur_bet = self.player_dict[id]

        bal -= cur_bet
        cur_bet = 0
        self.player_dict[id] = [bal, cur_bet]
        return bal
    
    def won_bet(self, mult, id):
        bal, cur_bet = self.player_dict[id]

        bal += mult * cur_bet
        self.player_dict[id] = [bal, cur_bet]
        return bal
    
    def prompt_wager(self, id):
        bet = get_int_response("How much would you like to wager? ")
        bal, _ = self.player_dict[id]
        while bet > bal:
            bet = get_int_response(f"You do not have enough in your balance to wager this amount (you have {bal}). ")
        
        self.player_dict[id][1] = bet

    def __str__(self):
        return f"balances: {self.player_dict}"