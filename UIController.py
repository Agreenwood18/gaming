import asyncio
import threading
from typing import Self
from User import User
from time import sleep
import datetime


#TODO: add input() to this
#TODO: add select from list to this
#TODO: timeout waiting on player response (TCP)


class UIController:
    # NOTE using asycio to gather responses from users
    #      because we are mostly waiting on slow I/O responses and its easy to handle results, because coroutines are in the same thread
    #      threading module does not take advantage of multi-core processors (multiprocessing module can handle that)

    def __init__(self, users: list[User]=[], message_delay_s=1) -> None:
        self.__current_players_for_msg: list[str] = []
        self.__current_msg: str | None = None
        self.__time_to_send_next: datetime.datetime = datetime.datetime.now()
        self.message_delay_s: int = message_delay_s
        self.player_to_user_map: dict[str, User] = dict()

        from UserRouter import UserRouter
        self.router_loop: asyncio.AbstractEventLoop = UserRouter().loop
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
            asyncio.run(self.player_to_user_map[player_id].send_message(msg))

        self.__prepare_for_next_send()

    ## returns the index of the selected item from the list
    def waitfor_selection(self, item_list: list) -> list[int | None]:
        # TODO: handle multiple players
        self.__current_msg += "".join([f"\n\t{i+1}. {item}" for i, item in enumerate(item_list)])
        return [num - 1 if num != None else None for num in self.waitfor_int(range_inclusive=(1, len(item_list)))]
        

        while True:
            if 0 < selected_val <= len(item_list):
                return selected_val - 1 # return the actual index
            self.delay_next(0).whisper_this_to(f"You must enter a number between 0 and {len(item_list)}")

    ## NOTE: not affected by time delay (usually things that need a response should be immediate)
    def waitfor_yes_no(self) -> list[bool | None]:
        # TODO: handle multiple players
        # self.__check_send_allowed()

        res = [x == 0 if x != None else x for x in self.waitfor_selection(["yes", "no"])]

        # self.__prepare_for_next_send()
        return res

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
        async def async_helper():


            # TODO: using a task group is safer and simpler: with task group as tg... asyncio.TaskGroup.create_task() 
# async with asyncio.TaskGroup() as tg:
#         task1 = tg.create_task(some_coro(...))
#         task2 = tg.create_task(another_coro(...))
#     print(f"Both tasks have completed now: {task1.result()}, {task2.result()}")




            tasks: list[asyncio.Task] = []
            for i, player_id in enumerate(self.__current_players_for_msg):
                print(f"creating task {i+1}")
                tasks.append(asyncio.create_task(self.__retry_until_int(self.__format_message(self.__current_msg), player_id, range_inclusive), name=i))

            done: set[asyncio.Task]
            pending: set[asyncio.Task]
            print("waiting")
            done, pending = await asyncio.wait(tasks) # TODO , timeout=5

            for task in pending:
                if not task.cancel():
                    done.add(task)
            
            res: list[int | None] = [None] * len(self.__current_players_for_msg)
            for task in done:
                try:
                    result = int(task.result())
                    index = int(task.get_name())
                    res[index] = result
                except Exception as e:
                    print(f"ERROR occurred... but why?: {e}")
            
            return res
            

        # val: int = self.__retry_until_int(self.__format_message(self.__current_msg), self.__current_players_for_msg[0], range_inclusive=range_inclusive)
        

        self.__check_send_allowed()

        res: list[int | None]

        try:
            my_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            if my_loop == self.router_loop:
                res = asyncio.run(async_helper())
            else:
                raise RuntimeError("go to exception!!")
        except Exception:
            res = asyncio.run_coroutine_threadsafe(async_helper(), self.router_loop).result()

        self.__prepare_for_next_send()

        return res

    ##################### PRIVATE METHODS #####################

    async def __retry_until_int(self, formatted_msg: str, player_id: str, range_inclusive: tuple[int, int]) -> int:
        print("retry inting with:", player_id)
        user: User = self.player_to_user_map[player_id]
        await user.send_message(formatted_msg)
        val = await user.receive_message()
        # val = input(formatted_msg).strip()
        while True:
            if not val.isdigit():
                await user.send_message("please enter an integer value: ")
                val = await user.receive_message()
                # val = input("please enter an integer value: ").strip()
            elif range_inclusive == None or (range_inclusive != None and range_inclusive[0] <= int(val) <= range_inclusive[1]):
                # success!
                return int(val)
            else:
                await user.send_message(f"please enter an integer within this range: {range_inclusive}")
                val = await user.receive_message()
                # val = input(f"please enter an integer within this range: {range}").strip()

    def __send_message(self) -> None | ValueError:
        pass

    def __format_message(self, msg: any) -> str:
        end_str: str = "\n\n"
        try:
            return str(msg) + end_str
        except:
            return end_str

    def __sleep_until_delay(self) -> None:
        time_to_wait: datetime.timedelta = max(0, (self.__time_to_send_next - datetime.datetime.now()).total_seconds())
        sleep(time_to_wait) # thread-safe

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
