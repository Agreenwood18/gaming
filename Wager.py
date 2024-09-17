class Wager():
    def __init__(self):
        self.current_bet = 0
        self.balance = 0
        self.minBal = 100
        self.maxBal = 300

    def starting_Bal(self):
        self.balance = int(input("What would you like your balance to be, (anywhere from 100 - 300): "))
        while self.balance < self.minBal or self.balance > self.maxBal:
            self.balance = int(input("That amount is not allowed, please select an amount between 100 and 300"))

        return self.balance
    
    def lost_bet(self):
        self.balance -= self.current_bet
        return self.balance
    
    def won_bet(self, mult):
        self.balance += (mult*self.current_bet)
        return self.balance
    
    def prompt_wager(self):
        bet = int(input("How much would you like to wager? "))
        while bet > self.balance:
            bet = int(input("You do not have enough in your balance to wager this amount."))
        self.current_bet = bet

    def __str__(self):
        return f"balance: {self.balance}"