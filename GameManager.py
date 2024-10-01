from Blackjack.BlackJackGame import BlackJack
from Game import Game
from UIController import UIController
from User import User
from util import get_int_response


## We can kind of think of this like the lobby for users
## people will stay in here and play various games
class GameManager:
    def __init__(self, users) -> None:
        self.current_game: Game = None
        self.users: list[User] = users
        self.UI_controller: UIController = UIController(users)
    
    def game_selecter(self) -> None:
        while True:
            gameType = get_int_response("What game would you like to play? (select 1 to see list or enter the number of the game is you already know): ")
            match gameType:
                case 1:
                    gameType = get_int_response("1 for repeat list, 2 for Black Jack")
                    break
                case 2:
                    player_ids: list[str | None] = [u.player_id for u in self.users]
                    self.current_game = BlackJack(player_ids)
                    break
                case _:
                    print(f"{gameType} is a whore for not being a game option.\n\tBut... unfortunately we can't do much about that (select again dumbass)\n")
                    
        self.current_game.start()
