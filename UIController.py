from typing import Self
from User import User
from time import sleep
import datetime

#TODO: add input() to this
#TODO: add select from list to this
#TODO: timeout waiting on player response (TCP)


class UIController:
    def __init__(self, users: list[User]=[], message_delay_s=1) -> None:
        self.time_to_send_next: datetime.datetime = datetime.datetime.now()
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

    ## sets the delay, allowing the next message to be sent whenever
    ## returns self, allowing to immediately chain another method onto the call
    ## usage (send a message immediately):
    ##         ui_cont_instance.delay_next(0).whisper_this_to("I just employed method chaining", friend_o)
    def delay_next(self, seconds: int) -> Self:
        self.__set_next_send_time(seconds)
        return self

    ## whisper to every player passed in
    def whisper_this_to(self, msg: str, *player_ids) -> None:
        #TODO: for id in player_ids:
        self.__sleep_until_delay()
        print(self.__format_message(msg))
        self.__set_next_send_time()

    def broadcast_to_all(self, msg: any="") -> None:
        self.__sleep_until_delay()
        print(self.__format_message(msg))
        self.__set_next_send_time()

    ## returns the index of the selected item from the list
    def select_from_list(self, question: str, item_list: list, player_id: str) -> int:
        list_msg: str = "".join([f"\n\t{i+1}. {item}" for i, item in enumerate(item_list)])
        while True:
            selected_val = self.get_int_response(question + list_msg, player_id)
            if 0 < selected_val <= len(item_list):
                return selected_val - 1 # return the actual index
            self.delay_next(0).whisper_this_to(f"You must enter a number between 0 and {len(item_list)}")

    ## NOTE: not affected by time delay (usually things that need a response should be immediate)
    def prompt_yes_or_no(self, question, player_id) -> bool:
        while True:
            response = input(f"{question} (1: yes / 2: no): ").strip()
            if response == '1':
                print()
                return True
            elif response == '2':
                print()
                return False

    ## NOTE: not affected by time delay (usually things that need a response should be immediate)
    def get_int_response(self, question, player_id) -> int:
        val = input(self.__format_message(question)).strip()
        while True:
            if val.isdigit():
                print()
                return int(val)
            val = input("please enter an integer value: ").strip()

    ## this is a private method that should not be accessed outside
    def __format_message(self, msg: any) -> str:
        end_str: str = "\n\n"
        try:
            return str(msg) + end_str
        except:
            return end_str

    def __sleep_until_delay(self) -> None:
        time_to_wait: datetime.timedelta = max(0, (self.time_to_send_next - datetime.datetime.now()).total_seconds())
        sleep(time_to_wait)

    def __set_next_send_time(self, delay_override=None) -> None:
        self.time_to_send_next = datetime.datetime.now() + datetime.timedelta(seconds=( delay_override if delay_override != None else self.message_delay_s ))