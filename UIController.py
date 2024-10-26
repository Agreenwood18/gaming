import time
from User import User
from enum import Enum
from typing import Any, Callable, Optional, Self
import asyncio
import datetime

from myglobals import myglobals


#TODO: add input() to this
#TODO: add select from list to this
#TODO: timeout waiting on player response (TCP)

class MessageResponse(Enum):
    no_response = 0
    int = 1
    yes_no = 2
    selection = 3
    string = 4

class Message:
    ## NOTE: if `whisper_to` is not specified, the msg will be broadcasted to all but the excluded

    def __init__(self, msg: str) -> None:
        ## NOTE msg is able to be modified with a builder method, because other methods rely on changing the users already existing str
        self.msg: str = msg
        self.whispers: set[str] = set()
        self.excluded: set[str] = set()
        self.range_inclusive: tuple[int, int] = tuple()
        self.response_type: MessageResponse = MessageResponse.no_response
    
    ## whisper to each player passed in
    def whisper_to(self, *player_ids:str) -> Self:
        # TODO: what if player id isn't part of the controller?
        if len(player_ids) == 1 and isinstance(player_ids[0], list):
            # allow caller to pass in a list or comma separated player ids
            player_ids = player_ids[0]
        self.whispers = set(player_ids)
        return self

    ## NOTE only intended to be used without a whisper (to exclude from a broadcast)
    def exclude(self, *player_ids:str) -> Self:
        if len(player_ids) == 1 and isinstance(player_ids[0], list):
            # allow caller to pass in a list or comma separated player ids
            player_ids = player_ids[0]
        self.excluded = set(player_ids)
        return self

    def waitfor_int(self, range_inclusive: tuple[int, int] | None = None) -> Self:
        self.msg += f" Between {range_inclusive[0]} and {range_inclusive[1]}" if range_inclusive != None else ""
        self.range_inclusive = range_inclusive
        self.response_type = MessageResponse.int
        return self

    def waitfor_yes_no(self) -> Self:
        self.waitfor_selection(["yes", "no"])
        self.response_type = MessageResponse.yes_no # after ^ waitfor_selection ^ call to overwrite that
        self.range_inclusive = (1,2)
        return self

    def waitfor_selection(self, item_list: list) -> Self:
        self.msg += "".join([f"\n\t{i+1}. {item}" for i, item in enumerate(item_list)])
        self.response_type = MessageResponse.selection
        self.range_inclusive = (1, len(item_list))
        return self
    
    def waitfor_string(self) -> Self:
        self.response_type = MessageResponse.string
        return self



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
        self.__active_tasks: list[asyncio.Task] = []

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

   

    ##################### SEND BUILT MESSAGE METHODS #####################

    
    ######### TODO TODO TODO TODO:
    #                                           send() needs to -> list[tuple[str, None | any]]
    #                                           orrrrr.... it returns self and you can call a results() method for it (its saved to self.)
    #                                           this allows us to have helper methods chained like all(true), percent(true, .5), etc
    #                                           take in *msgs, do them all in different asyncio's, calling some private __handle_msg
    # for task in done:
    #     try:
    #         result = int(task.result())
    #         index = int(task.get_name())
    #         res[index] = result
    #         print(f"Player {self.get_broadcast_list()[index]} just responded with int: {result}")
    #     except Exception as e:
    #         print(f"ERROR occurred... but why?: {e}")
    
    # return res
    
    def send(self, *messages: Message) -> dict[str, Optional[Any]]:

        # msg: str = self.__format_message(self.__current_msg)
        # for player_id in self.__current_players_for_msg:
        #     asyncio.run(self.player_to_user_map[player_id].send_message(msg))

        if len(messages) == 1 and isinstance(messages[0], list):
            # allow caller to pass in a list or comma separated Messages
            messages = messages[0]

        if not len(messages):
            # probably passed in an empty list
            return

        self.__sleep_until_delay()

        res: dict[str, Optional[Any]]


        try:
            my_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            if my_loop == myglobals.router_loop:
                raise RuntimeError("You should be awaiting async_send instead...")
        except Exception:
            pass

        res = asyncio.run_coroutine_threadsafe(self.__send_concurrent_msgs(messages), myglobals.router_loop).result()

        self.__prepare_for_next_send()

        print(f'\nmessage results for {[m.msg for m in messages]}. current players in UI: {self.player_to_user_map.keys()}\n\n', res, '\n\n')

        return res
    
    async def async_send(self, *messages: Message) -> dict[str, Optional[Any]]:

        # msg: str = self.__format_message(self.__current_msg)
        # for player_id in self.__current_players_for_msg:
        #     asyncio.run(self.player_to_user_map[player_id].send_message(msg))

        if len(messages) == 1 and isinstance(messages[0], list):
            # allow caller to pass in a list or comma separated Messages
            messages = messages[0]

        if not len(messages):
            # probably passed in an empty list
            return

        self.__sleep_until_delay()

        res: dict[str, Optional[Any]]


        global myglobals
        try:
            my_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            if my_loop == myglobals.router_loop:
                res = await self.__send_concurrent_msgs(messages)
            else:
                raise RuntimeError("You should be calling send instead...")
        except Exception as e:
            raise RuntimeError("You should probably be calling send instead... here is the exception:", e)


        self.__prepare_for_next_send()

        print(f'\nmessage results for {[m.msg for m in messages]}. current players in UI: {self.player_to_user_map.keys()}\n\n', res, '\n\n')

        return res


















    def has_current_messages(self) -> bool:
        return any(self.__active_tasks)



    def cancel_current_messages(self):
        for task in self.__active_tasks:
            if not task.cancel():
                print("WARNING... this task should have been cancelled?", task)






    ##################### PRIVATE METHODS #####################

    async def __send_concurrent_msgs(self, messages: list[Message]) -> dict[str, Optional[Any]]:
        # TODO: using a task group is safer and simpler: with task group as tg... asyncio.TaskGroup.create_task() 
        # async with asyncio.TaskGroup() as tg:
        #         task1 = tg.create_task(some_coro(...))
        #         task2 = tg.create_task(another_coro(...))
        #     print(f"Both tasks have completed now: {task1.result()}, {task2.result()}")
        
        for msg in messages:
            ids_for_msg: set[str] = (msg.whispers if len(msg.whispers) else set(self.player_to_user_map.keys()))
            ids_for_msg = ids_for_msg - msg.excluded
            
            for player_id in ids_for_msg:
            
                match msg.response_type:
                    case MessageResponse.no_response:
                        self.__active_tasks.append(asyncio.create_task(self.player_to_user_map[player_id].send_message(self.__format_message(msg.msg)), name=player_id))
                    case MessageResponse.int:
                        self.__active_tasks.append(asyncio.create_task(self.__retry_until_int(self.__format_message(msg.msg), player_id, msg.range_inclusive), name=player_id))
                    case MessageResponse.yes_no:
                        # return true/false
                        yes_no_callback = lambda x:  bool(int(x) == 1) if x != None else None
                        self.__active_tasks.append(asyncio.create_task(self.__retry_until_int(self.__format_message(msg.msg), player_id, msg.range_inclusive, final_type_callback=yes_no_callback), name=player_id))
                    case MessageResponse.selection:
                        # return the index from the original selection list
                        yes_no_callback = lambda x:  int(int(x) - 1) if x != None else None
                        self.__active_tasks.append(asyncio.create_task(self.__retry_until_int(self.__format_message(msg.msg), player_id, msg.range_inclusive, final_type_callback=yes_no_callback), name=player_id))
                    case MessageResponse.string:
                        print("yep")
                        self.__active_tasks.append(asyncio.create_task(self.__get_string(self.__format_message(msg.msg), player_id), name=player_id))
                    case _:
                        raise RuntimeError("WHATTT EVEN HAPPENED!")


        done: set[asyncio.Task]
        pending: set[asyncio.Task]
        done, pending = await asyncio.wait(self.__active_tasks) # TODO , timeout=5

        res: dict[str, Optional[Any]] = dict()
        for task in pending:
            # try to cancel all; if no task to cancel, it must be done
            if not task.cancel():
                done.add(task)
            else:
                # empty response due to timeout ideally (or error?)
                res[task.get_name()] = None

        self.__active_tasks = []

        for task in done:
            try:
                result: Any = task.result()
                id: str = task.get_name()
                res[id] = result
            except Exception as e:
                print(f"ERROR occurred with task:\n{task}\n\n\tBut why?: {e}")
            
        return res

    async def __get_string(self, formatted_msg: str, player_id: str) -> str | None:
        user: User = self.player_to_user_map[player_id]
        print(1)
        await user.send_message(formatted_msg)
        print(2)
        r = await user.receive_message()
        return r



    async def __retry_until_int(self, formatted_msg: str, player_id: str, range_inclusive: tuple[int, int], final_type_callback: Callable | None=None) -> int | Any:
        ## `final_type_callback` allows you to have the final say on the type returned from this method
        
        user: User = self.player_to_user_map[player_id]
        await user.send_message(formatted_msg)
        val = await user.receive_message()
        # val = input(formatted_msg).strip()
        while True:
            if not val.isdigit():
                await user.send_message("please enter a number: ")
                val = await user.receive_message()
                # val = input("please enter an integer value: ").strip()
            elif range_inclusive == None or (range_inclusive != None and range_inclusive[0] <= int(val) <= range_inclusive[1]):
                # success!
                break
            else:
                await user.send_message(f"please enter a number within this range: {range_inclusive}")
                val = await user.receive_message()
                # val = input(f"please enter an integer within this range: {range}").strip()

        if final_type_callback != None:
            return final_type_callback(val)
        else:
            return int(val)

    ## returns the index of the selected item from the list
    async def __selection(self, formatted_msg: str, item_list: list) -> list[int | None]:
        return [num - 1 if num != None else None for num in self.waitfor_int(range_inclusive=(1, len(item_list)))]
        

        while True:
            if 0 < selected_val <= len(item_list):
                return selected_val - 1 # return the actual index
            self.delay_next(0).whisper_this_to(f"You must enter a number between 0 and {len(item_list)}")

    ## NOTE: not affected by time delay (usually things that need a response should be immediate)
    async def __yes_no(self) -> list[bool | None]:
        # TODO: handle multiple players
        # self.__check_send_allowed()

        res = [x == 0 if x != None else x for x in self.waitfor_selection(["yes", "no"])]

        # self.__prepare_for_next_send()
        return res


    def __format_message(self, msg: any) -> str:
        end_str: str = "\n\n"
        try:
            return str(msg) + end_str
        except:
            return end_str

    def __sleep_until_delay(self) -> None:
        time_to_wait: datetime.timedelta = max(0, (self.__time_to_send_next - datetime.datetime.now()).total_seconds())
        time.sleep(time_to_wait)

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
