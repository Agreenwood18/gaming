class Card:
    def __init__(self, val, suit, int_val = None):
        self.val = val
        self.int_val = None
        self.suit = suit

    def __str__(self):
        return f"{self.val}({self.suit})"
    
    def __int__(self):
        if isinstance(self.val, int):
            return self.val
        elif self.int_val != None:
            return self.int_val
        
        raise ValueError(f"need a value map key-val for {self.val}")
     