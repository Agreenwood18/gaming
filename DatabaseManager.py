import json
from dataclasses import asdict, dataclass, is_dataclass
import datetime


###### TODO: names are not currently unique
##              and dates



PLAYER_DB = 'players.json'



class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):

        if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
            return o.isoformat()
        elif isinstance(o, datetime.timedelta):
            return (datetime.datetime.min + o).time().isoformat()
        elif is_dataclass(o):
            return asdict(o)
        return super().default(o)


@dataclass
class PlayerSave:
    ## NOTE: if we ever do nested dataclasses we need to do this: https://stackoverflow.com/questions/69059290/how-to-unpack-nested-json-into-python-dataclass
    ## NOTE: do not change the order of these VVV
    unique_name: str
    money: int
    date_started: datetime
    date_ended: datetime


class DatabaseManager:
    def __init__(self):
        ## cached of the active players being used (easier to do adjustments and call to other methods in the class. reduces reads)
        ## { unique_name: { __ attributes of PlayerSave __ } }
        self.player_saves: dict = {}

    def get_all_unique_names(self):
        with open(PLAYER_DB, 'r') as file:
            player_save_json: json = json.load(file)["players"]
            return list(player_save_json)

    ## TODO: this player will stay in an array indefinitely (remove on logout)
    def get_player_save(self, unique_name) -> PlayerSave:
        player_save: PlayerSave = None

        if unique_name in self.player_saves:
            player_save = self.player_saves[unique_name]            
        else:
            with open(PLAYER_DB, 'r') as file:
                player_save_json = json.load(file)["players"][unique_name]
                player_save = PlayerSave(unique_name, player_save_json["money"], player_save_json["date_started"], player_save_json["date_ended"])
                self.player_saves[unique_name] = player_save # add to cache
        
        return player_save

    def create_player(self, unique_name, money=0) -> None:
        # t = datetime.datetime.now()
        t = 69
        player = PlayerSave(unique_name, money, t, t)
        self.player_saves[unique_name] = player # add to cache
        self.save_player(unique_name)
        return player

    def save_player(self, unique_name) -> None:
        # save just this player to json file
        player_save = self.get_player_save(unique_name)
        with open(PLAYER_DB, "r+") as file:

            file_json = json.load(file)
            file_json["players"][unique_name] = asdict(player_save)
            
            
            print("trying to write", file_json)
            file.seek(0)
            json.dump(file_json, file, indent=4)
            file.truncate()

        # file.close()

    ## add or remove money in the database
    ## NOTE: on error returns -1. Otherwise it returns new balance
    def adjust_money(self, increment: float, unique_name: str) -> int:
        player_save = self.get_player_save(unique_name)
        player_save.money += increment

        if player_save.money < 0:
            # increment not allowed
            player_save.money -= increment
            return -1
        
        self.save_player(unique_name)
        return player_save.money
