from Games import BlackJack, Game
from util import get_int_response


class GameManager:
    def __init__(self, player_ids):
        self.current_game: Game = None
        self.player_ids: list = player_ids
    
    def game_selecter(self):
        while True:
            gameType = get_int_response("What game would you like to play? (select 1 to see list or enter the number of the game is you already know): ")
            match gameType:
                case 1:
                    gameType = get_int_response("1 for repeat list, 2 for Black Jack")
                    break
                case 2:
                    self.current_game = BlackJack(self.player_ids)
                    break
                case _:
                    print(f"{gameType} is a whore for not being a game option.\n\tBut... unfortunately we can't do much about that (select again dumbass)\n")
                    
        self.current_game.start()
