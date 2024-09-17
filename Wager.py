class Wager():
    def __init__(self):
        self.balance = 0
        self.minBal = 100
        self.maxBal = 300

    def starting_Bal(self):
        self.balance = int(input("What would you like your balance to be, (anywhere from 100 - 300): "))
        while self.balance < self.minBal or self.balance > self.maxBal:
            self.balance = int(input("That amount is not allowed, please select an amount between 100 and 300"))

        return self.balance
    
    def lost_bet(self, bet):
        self.balance -= bet
        return self.balance
    
    def won_bet(self, bet, mult):
        print(f"\n\nBALANCE: {self.balance}, bet: {bet}, mult: {mult}\n\n")
        self.balance += (mult*bet)
        return self.balance
    
    def wagering(self):
        currentBet = int(input("How much would you like to wager? "))
        while currentBet > self.balance:
            currentBet = int(input("You do not have enough in your balance to wager this amount."))
        return currentBet