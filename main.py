from DatabaseManager import DatabaseManager
from GameManager import GameManager
import util

def starting_bal():
    minBal, maxBal = 100, 300
    bal = util.get_int_response("What would you like your balance to be, (anywhere from 100 - 300): ")
    while bal < minBal or bal > maxBal:
        bal = util.get_int_response("That amount is not allowed, please select an amount between 100 and 300: ")

    return bal

def main():
    DB_manager: DatabaseManager = DatabaseManager()

    print()

    player_ids = []
    for n in range(1, util.get_int_response("How many people are playing? ") + 1):
        save = None
        if util.prompt_yes_or_no(f"Is one of these you?\n\t{', '.join(DB_manager.get_all_unique_names())}\n"):
            save = DB_manager.get_player_save(input("Enter the name").strip())
        else:
            save = DB_manager.create_player(input("Enter the name of your new player").strip(), starting_bal())
            
        print(save)
        player_ids.append(save.unique_name)
        # starting_Bal(n)

    

    all_games: GameManager = GameManager(player_ids)
    all_games.game_selecter()

if __name__ == "__main__":
    main()
