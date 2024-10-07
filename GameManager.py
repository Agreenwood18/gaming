import queue
import threading
from BlackjackGame import BlackjackGame
from Game import Game
from UIController import UIController
from User import User


## We can kind of think of this like the lobby for users
## people will stay in here and play various games
class GameManager:
    def __init__(self, users: list[User]=[], name: str="Gamers-club") -> None:
        self.__user_queue: queue.SimpleQueue[User] = queue.SimpleQueue()
        # TODO: this ^^ is something... (maybe just newly added users...)
        self.users: list[User] = users

        self.current_game: Game = None
        self.UI_controller: UIController = UIController(users) ## in charge of keeping this up to date
        self.__thread_lock: threading.Lock = threading.Lock() # now with thread safety! maybe? TODO: unit test it my man
        self.name: str = name

    def start_lobby(self):
        try:
            while True:
                self.wait_in_lobby() # maybe leave or hop back into a new game? idk
                self.game_selector()
                self.start_game() # game finishes and you're kicked back out to the lobby
        finally:
            pass
            # TODO: all of em: user_socket.close()

    def add_user(self, user: User) -> None:
        with self.__thread_lock: # TODO: do I even need this ?
            self.__user_queue.put(user) # TODO: is this overcomplicated ?
            self.UI_controller.add_user(user) # TODO: uhh does this need to be threadsafe ?

    def remove_user(self, user: User) -> None:
        with self.__thread_lock:
            self.users.remove(user)
            self.UI_controller.remove_user(user)

    def wait_in_lobby(self) -> None:
        while True:
            try:
                new_user = self.__user_queue.get(True, 0.1)
                # new user joined!!
                self.users.append(new_user)
                self.UI_controller.create_msg(f"EVERYBODY WELCOME {new_user.player_id}, the {len(self.users)}th player to spend their time in \"{self.name}\"!!!").broadcast().send()
            except:
                # no new users...
                pass

            if len(self.users) and all(x == 1 for x in self.UI_controller.create_msg("uhhhh... everyone press 1 to start playing").broadcast().waitfor_int()):
                return

    def game_selector(self) -> None:
        while True:
            games: list[str] = ["Blackjack", "dummy option"]
            gameType: list[int | None] = self.UI_controller.create_msg("What game would you like to play?").broadcast().waitfor_selection(games)
            if not all(x==gameType[0] for x in gameType): # if not all the same
                self.UI_controller.create_msg("You guys need to pick the same game... figur it out").broadcast().send()
                continue

            # they reached an agreement...
            match games[gameType[0]]:
                case "Blackjack":
                    player_ids: list[str | None] = [u.player_id for u in self.users]
                    self.current_game = BlackjackGame(player_ids, self.UI_controller)
                    break
                case _: # this should never be reached
                    self.UI_controller.create_msg(f"The developers should be ashamed that {gameType} is not a game option.\n\tBut... unfortunately we can't do much about that (select again dumbass)\n").broadcast().send()
                    
    def start_game(self) -> None:
        self.current_game.start()
