import asyncio
import threading

from DatabaseManager import DatabaseManager, PlayerSave
from GameManager import GameManager
from UIController import Message, UIController
from User import User
from util import SingletonClass


class LobbyManager(SingletonClass):
    def __init__(self) -> None:
        self.lobbies: dict[str, GameManager] = {}
        # self.__thread_lock: threading.Lock = threading.Lock() # now with thread safety! maybe? TODO: unit test it my man
        self.DB_manager: DatabaseManager = DatabaseManager()

    def manage_user(self, new_user: User) -> None:
        def thread_helper() -> None:
            temp_UI_controller = UIController(users=[new_user], message_delay_s=0)

            
            temp_UI_controller.send(Message("welcome to the game thumbass"))

            # user selects a player save
            save: PlayerSave | None = None
            player_options: list[str] = self.DB_manager.get_all_unique_names()
            player_options.append("no... (create new)")
            player_index: int = temp_UI_controller.send(Message("Is one of these you?").waitfor_selection(player_options))[new_user.player_id]
            if player_index != len(player_options) - 1:
                save = self.DB_manager.get_player_save(player_options[player_index])
            else: # create new player
                save = self.DB_manager.create_player(input("Enter the name of your new player").strip(), self.starting_bal(temp_UI_controller, new_user.player_id))
                
            # user has chosen their player
            new_user.start_using_player(save.unique_name)

            temp_UI_controller.send(Message(f"This is you {save}"))
            # while True:
            #     msg = new_user.receive_message()
            #     if msg:
            #         new_user.send_message("YOU SAID THIS!?!" + msg)
            #     else:
            #         print("WHAT HAPPEND")
            #         break
            self.__get_or_create_lobby().add_user(new_user)
        
        threading.Thread(target=thread_helper).start() #TODO: this should most definitely be asyncio task

    def starting_bal(self, UI_controller: UIController, player_id) -> int:
        minBal, maxBal = 100, 300
        bal = UI_controller.waitfor_int("What would you like your balance to be, (anywhere from 100 - 300): ", player_id)
        while bal < minBal or bal > maxBal:
            bal = UI_controller.waitfor_int("That amount is not allowed, please select an amount between 100 and 300: ", player_id)

        return bal

    def __get_or_create_lobby(self) -> GameManager:
        lobby_id = 99999 # TODO: make random and meaningful for multiple lobbies
        if lobby_id not in self.lobbies:
            new_lobby = GameManager()
            self.lobbies[lobby_id] = new_lobby
            # asyncio.run(new_lobby.start_lobby())
            threading.Thread(target=new_lobby.start_lobby).start() # TODO: save threads and kill them? idk
        return self.lobbies[lobby_id]
