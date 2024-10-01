from DatabaseManager import DatabaseManager, PlayerSave
from GameManager import GameManager
from User import User
import util

def starting_bal() -> int:
    minBal, maxBal = 100, 300
    bal = util.get_int_response("What would you like your balance to be, (anywhere from 100 - 300): ")
    while bal < minBal or bal > maxBal:
        bal = util.get_int_response("That amount is not allowed, please select an amount between 100 and 300: ")

    return bal

def main() -> any:
    DB_manager: DatabaseManager = DatabaseManager() ## THE instance ;)

    player_ids: list[str] = []
    for _ in range(1, util.get_int_response("How many people are playing? ") + 1):
        save: PlayerSave | None = None
        if util.prompt_yes_or_no(f"Is one of these you?\n\t{', '.join(DB_manager.get_all_unique_names())}\n"):
            save = DB_manager.get_player_save(input("Enter the name").strip())
        else:
            save = DB_manager.create_player(input("Enter the name of your new player").strip(), starting_bal())
            
        print(save)
        player_ids.append(save.unique_name)
    
    all_games: GameManager = GameManager([User(id) for id in player_ids])
    all_games.game_selecter()

    DB_manager.save_all()


if __name__ == "__main__":
    main()
