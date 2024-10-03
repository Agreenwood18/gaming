from User import User


class UIController:
    def __init__(self, users: list[User]) -> None:
        self.player_to_user_map: dict[str, User] = dict()
        for u in users:
            self.player_to_user_map[u.player_id] = u

    ## whisper to every player passed in
    def whisper_this_to(self, msg: str, *player_ids) -> None:
        #TODO: for id in player_ids:
        print(self.__format_message(msg))

    def broadcast_to_all(self, msg: str) -> None:
        print(self.__format_message(msg))

    ## this is a private method that should not be accessed outside
    def __format_message(self, str="") -> str:
        return str + "\n\n"
