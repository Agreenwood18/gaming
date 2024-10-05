from typing import Self
from User import User
from time import sleep
import datetime

#TODO: add input() to this
#TODO: add select from list to this
#TODO: timeout waiting on player response (TCP)


class UIController:
    def __init__(self, users: list[User]=[], message_delay_s=1) -> None:
        self.__current_players_for_msg: list[str] = []
        self.__current_msg: str | None = None
        self.__time_to_send_next: datetime.datetime = datetime.datetime.now()
        self.message_delay_s: int = message_delay_s
        self.player_to_user_map: dict[str, User] = dict()
        for u in users:
            self.add_user(u)

    def add_user(self, user: User) -> None:
        self.player_to_user_map[user.player_id] = user

    def remove_user(self, user: User) -> None:
        # even if a user changes players/changes their players name
        if user.player_id in self.player_to_user_map:
            # the easy way
            del self.player_to_user_map[user.player_id]
        else:
            # the hard way
            for player_id, user in self.player_to_user_map.items():
                if user is user:
                    del self.player_to_user_map[player_id]
                    return
            
            raise ValueError(f"User is not a part of this UIController: {self.player_to_user_map}")

    ##################### GENERIC BUILDER METHODS #####################

    ## sets the delay, allowing the next message to be sent whenever
    ## returns self, allowing to immediately chain another method onto the call
    ## usage (send a message immediately):
    ##         ui_cont_instance.delay_next(0).whisper_this_to("I just employed method chaining", friend_o)
    def delay_next(self, seconds: int) -> Self: # TODO: change to `set_delay` and adjust comments above
        self.__time_to_send_next = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        return self

    def create_msg(self, msg: str) -> Self | ValueError:
        if self.__current_msg != None:
            raise ValueError("Previous message was created but not sent! Be sure to complete your chain with any `send_` or `waitfor_` method")
        
        self.__current_msg = msg
        return self

    ## whisper to every player passed in
    def whisper_to(self, *player_ids:str) -> Self:
        # TODO: what if player id isn't part of the controller?
        self.__current_players_for_msg =  list(player_ids)
        return self

    def broadcast(self) -> Self:
        self.__current_players_for_msg = list(self.player_to_user_map.keys())
        return self

    ##################### SEND BUILT MESSAGE METHODS #####################

    def send(self) -> None | ValueError:
        self.__check_send_allowed()

        self.__sleep_until_delay()
        msg: str = self.__format_message(self.__current_msg)
        for player_id in self.__current_players_for_msg:
            self.player_to_user_map[player_id].send_message(msg)

        self.__prepare_for_next_send()

    ## returns the index of the selected item from the list
    def waitfor_selection(self, item_list: list) -> list[int | None]:
        # TODO: handle multiple players
        self.__current_msg += "".join([f"\n\t{i+1}. {item}" for i, item in enumerate(item_list)])
        return [num - 1 for num in self.waitfor_int(range_inclusive=(1, len(item_list)))]
        

        while True:
            if 0 < selected_val <= len(item_list):
                return selected_val - 1 # return the actual index
            self.delay_next(0).whisper_this_to(f"You must enter a number between 0 and {len(item_list)}")

    ## NOTE: not affected by time delay (usually things that need a response should be immediate)
    def waitfor_yes_no(self) -> list[bool | None]:
        # TODO: handle multiple players
        self.__check_send_allowed()
        user: User = self.player_to_user_map[self.__current_players_for_msg[0]]

        res = False
        while True:
            user.send_message(self.__format_message(f"{self.__current_msg} (y / n): "))
            response = user.receive_message()
            # response = input(f"{self.__current_msg} (y / n): ").strip()
            if response == 'y':
                res = True
                break
            elif response == 'n':
                res = False
                break

        self.__prepare_for_next_send()
        return res

    ## NOTE: not affected by time delay (usually things that need a response should be immediate)
    def waitfor_int(self, range_inclusive: tuple[int, int] | None = None) -> list[int | None]:
        self.__check_send_allowed()

        # TODO: handle multiple players
        val: int = self.__retry_until_int(self.__format_message(self.__current_msg), self.__current_players_for_msg[0], range_inclusive=range_inclusive)
        
        self.__prepare_for_next_send()
        return [val]

    ##################### PRIVATE METHODS #####################

    def __retry_until_int(self, formatted_msg: str, player_id: str, range_inclusive: tuple[int, int] | None = None) -> int:
        user: User = self.player_to_user_map[player_id]
        user.send_message(formatted_msg)
        val = user.receive_message()
        # val = input(formatted_msg).strip()
        while True:
            if not val.isdigit():
                user.send_message("please enter an integer value: ")
                val = user.receive_message()
                # val = input("please enter an integer value: ").strip()
            elif range_inclusive == None or (range_inclusive != None and range_inclusive[0] <= int(val) <= range_inclusive[1]):
                # success!
                return int(val)
            else:
                user.send_message(f"please enter an integer within this range: {range_inclusive}")
                val = user.receive_message()
                # val = input(f"please enter an integer within this range: {range}").strip()

    def __send_message(self) -> None | ValueError:
        pass

    ## this is a private method that should not be accessed outside
    def __format_message(self, msg: any) -> str:
        end_str: str = "\n\n"
        try:
            return str(msg) + end_str
        except:
            return end_str

    def __sleep_until_delay(self) -> None:
        time_to_wait: datetime.timedelta = max(0, (self.__time_to_send_next - datetime.datetime.now()).total_seconds())
        sleep(time_to_wait)

    def __prepare_for_next_send(self) -> None:
        self.__time_to_send_next = datetime.datetime.now() + datetime.timedelta(seconds=self.message_delay_s)
        self.__current_msg = None
        self.__current_players_for_msg = []

    def __check_send_allowed(self) -> None | ValueError:
        problems = []
        if self.__current_msg == None:
            problems.append("You can't send a communication without a message! Be sure to start your chain with `create_msg` method")
        if not len(self.__current_players_for_msg):
            problems.append("You can't send a communication to nobody! Be sure to add `whisper` or `broadcast` to your method chain")
