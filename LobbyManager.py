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
        self.__get_or_create_lobby() # start thread

    async def manage_user(self, new_user: User) -> None:
        temp_UI_controller = UIController(users=[new_user], message_delay_s=0)
        
        await temp_UI_controller.async_send(Message("welcome to the game thumbass"))

        # user selects a player save
        save: PlayerSave | None = None
        player_options: list[str] = self.DB_manager.get_all_unique_names()
        player_options.append("no... (create new)")
        player_index: int = ( await temp_UI_controller.async_send(Message("Is one of these you?").waitfor_selection(player_options)) )[new_user.player_id]
        if player_index != len(player_options) - 1:
            save = self.DB_manager.get_player_save(player_options[player_index])
        else: # create new player

            print("new char creation")
            new_p_id = ( await temp_UI_controller.async_send(Message("Enter the name of your new player").waitfor_string()) ).popitem()[1]
            starting_bal = ( await temp_UI_controller.async_send(Message("What would you like your balance to be, (anywhere from 100 - 300): ").waitfor_int((100, 300))) ).popitem()[1]
            save = self.DB_manager.create_player(new_p_id, starting_bal)
            
        # user has chosen their player
        new_user.start_using_player(save.unique_name)

        await temp_UI_controller.async_send(Message(f"This is your save: {save}"))


        lobby_i = (await temp_UI_controller.async_send(Message("Which lobby?").waitfor_selection([item[1].name for item in self.lobbies.items()]))).popitem()[1]
        self.lobbies[list(self.lobbies.keys())[lobby_i]].add_user(new_user)
        # self.__get_or_create_lobby().add_user(new_user) TODOODODODOD TODO


    def __get_or_create_lobby(self) -> GameManager:
        lobby_id = 99999 # TODO: make random and meaningful for multiple lobbies
        if lobby_id not in self.lobbies:
            new_lobby = GameManager()
            self.lobbies[lobby_id] = new_lobby
            # asyncio.run(new_lobby.start_lobby())
            threading.Thread(target=new_lobby.start_lobby).start() # TODO: save threads and kill them? idk
        return self.lobbies[lobby_id]
