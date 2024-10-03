from Blackjack.BlackjackGame import Blackjack
from Game import Game
from UIController import UIController
from User import User


## We can kind of think of this like the lobby for users
## people will stay in here and play various games
class GameManager:
    def __init__(self, users: list[User]) -> None:
        self.current_game: Game = None
        self.users: list[User] = users
        self.UI_controller: UIController = UIController(users) ## in charge of keeping this current
    
    def game_selecter(self) -> None:
        while True:
            gameType = self.UI_controller.get_int_response("What game would you like to play? (select 1 to see list or enter the number of the game is you already know): ", (self.users[0]).player_id)
            match gameType:
                case 1:
                    gameType = self.UI_controller.get_int_response("1 for repeat list, 2 for Black Jack", self.users[0].player_id)
                    break
                case 2:
                    player_ids: list[str | None] = [u.player_id for u in self.users]
                    self.current_game = Blackjack(player_ids, self.UI_controller)
                    break
                case _:
                    print(f"{gameType} is a whore for not being a game option.\n\tBut... unfortunately we can't do much about that (select again dumbass)\n")
                    
        self.current_game.start()
