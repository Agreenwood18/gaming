import threading
from BlackjackGame import BlackjackGame
from Game import Game
from UIController import UIController
from User import User


## We can kind of think of this like the lobby for users
## people will stay in here and play various games
class GameManager:
    def __init__(self, users: list[User], name: str="Gamers-club") -> None:
        self.current_game: Game = None
        self.users: list[User] = users
        self.UI_controller: UIController = UIController(users) ## in charge of keeping this up to date
        self.__thread_lock: threading.Lock = threading.Lock() # now with thread safety! maybe? TODO: unit test it my man
        self.lobby_name: str = name

    def add_user(self, user: User) -> None: # TODO: more logic...
        with self.__thread_lock:
            self.users.append(user)
            self.UI_controller.add_user(user)

    def remove_user(self, user: User) -> None: # TODO: more logic...
        with self.__thread_lock:
            self.users.remove(user)
            self.UI_controller.remove_user(user)

    def wait_in_lobby(self) -> None:
        cur_user_num: int = len(self.users)
        while True:
            actual_U_num: int = len(self.users)
            for i in range(actual_U_num - cur_user_num):
                # new user joined!!
                self.UI_controller.broadcast_to_all(f"EVERYBODY WELCOME {self.users[ -(i + 1) ].player_id}, the {cur_user_num + i + 1}th player to spend their time in \"{self.lobby_name}\"!!!")
            
            cur_user_num = actual_U_num
            if cur_user_num and self.UI_controller.prompt_yes_or_no("This is a terrible way to do this!!! Continue loop to check for new user?", self.users[0]):
                return

    def game_selector(self) -> None:
        while True:
            games: list[str] = ["Blackjack"]
            gameType: int = self.UI_controller.select_from_list(f"What game would you like to play?", games, (self.users[0]).player_id)
            match games[gameType]:
                case "Blackjack":
                    player_ids: list[str | None] = [u.player_id for u in self.users]
                    self.current_game = BlackjackGame(player_ids, self.UI_controller)
                    break
                case _: # this should never be reached
                    self.UI_controller.broadcast_to_all(f"The developers should be ashamed that {gameType} is not a game option.\n\tBut... unfortunately we can't do much about that (select again dumbass)\n")
                    
    def start_game(self) -> None:
        self.current_game.start()
