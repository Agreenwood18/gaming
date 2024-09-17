class Card:
    def __init__(self, val, suit, int_val = None):
        ## int_val is decided on in the constructor
        ## int_val defaults to val

        self.val = val
        self.suit = suit

        if isinstance(self.val, int):
            self.int_val = self.val
        elif int_val != None:
            self.int_val = int_val
        else:
            raise ValueError(f"need a value map key-val for {self.val}, instead of {int_val}")


    def __str__(self):
        return f"{self.val}({self.suit})"
    
    def __int__(self):
        return self.int_val
    
    def __add__(self, other):
        return self.__int__() + other.__int__()

    def __radd__(self, other):
        return self.__add__(other)
