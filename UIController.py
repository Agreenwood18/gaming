from typing import Self
from User import User
from time import sleep
import datetime

#TODO: add input() to this
#TODO: add select from list to this


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
            
    ## resets the delay, allowing the next message to immediately be sent
    ## returns self, allowing to immediately chain another method onto the call
    ## usage (send a message immediately):
    ##         ui_cont_instance.reset_delay().whisper_this_to("I just employed method chaining", friend_o)
    def reset_delay(self) -> Self:
        self.time_to_send_next = datetime.datetime.now()
        return self

    ## whisper to every player passed in
    def whisper_this_to(self, msg: str, *player_ids) -> None:
        #TODO: for id in player_ids:
        time_to_wait: datetime.timedelta = max(0, (self.time_to_send_next - datetime.datetime.now()).total_seconds())
        sleep(time_to_wait)
        print(self.__format_message(msg))
        self.__set_next_send_time()

    def broadcast_to_all(self, msg: any="") -> None:
        time_to_wait: datetime.timedelta = max(0, (self.time_to_send_next - datetime.datetime.now()).total_seconds())
        sleep(time_to_wait)
        print(self.__format_message(msg))
        self.__set_next_send_time()

    def prompt_yes_or_no(self, question, player_id) -> bool:
        while True:
            response = input(f"{question} (1: yes / 2: no): ").strip()
            if response == '1':
                print()
                return True
            elif response == '2':
                print()
                return False

    def get_int_response(self, question, player_id) -> int:
        val = input(question).strip()
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

    def __set_next_send_time(self) -> None:
        self.time_to_send_next = datetime.datetime.now() + datetime.timedelta(seconds=self.message_delay_s)