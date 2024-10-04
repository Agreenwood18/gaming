from BlackjackGame import BlackjackGame
from Game import Game
from UIController import UIController
from User import User


## We can kind of think of this like the lobby for users
## people will stay in here and play various games
class GameManager:
    def __init__(self, users: list[User]) -> None:
        self.current_game: Game = None
        self.users: list[User] = users
        self.UI_controller: UIController = UIController(users) ## in charge of keeping this up to date
    
    def game_selecter(self) -> None:
        while True:
            games: list[str] = ["Blackjack"]
            gameType = self.UI_controller.select_from_list(f"What game would you like to play?", games, (self.users[0]).player_id)
            match games[gameType]:
                case "Blackjack":
                    player_ids: list[str | None] = [u.player_id for u in self.users]
                    self.current_game = BlackjackGame(player_ids, self.UI_controller)
                    break
                case _: # this should never be reached
                    print(f"{gameType} is a whore for not being a game option.\n\tBut... unfortunately we can't do much about that (select again dumbass)\n")
                    
        self.current_game.start()
