from DatabaseManager import DatabaseManager, PlayerSave
from GameManager import GameManager
from UIController import UIController
from User import User

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'Blackjack'))

def starting_bal(UI_controller, player_id) -> int:
    minBal, maxBal = 100, 300
    bal = UI_controller.get_int_response("What would you like your balance to be, (anywhere from 100 - 300): ", player_id)
    while bal < minBal or bal > maxBal:
        bal = UI_controller.get_int_response("That amount is not allowed, please select an amount between 100 and 300: ", player_id)

    return bal

def main() -> any:
    DB_manager: DatabaseManager = DatabaseManager() ## THE instance ;)
    lobby_UI_controller: UIController = UIController()

    # a user "connects" with their own terminal
    connected_user = User("unassigned_player")
    lobby_UI_controller.add_user(connected_user)

    # user selects a player save
    save: PlayerSave | None = None
    player_options: list[str] = DB_manager.get_all_unique_names()
    player_options.append("no. (create new)")
    player_index: int = lobby_UI_controller.select_from_list(f"Is one of these you?", player_options, connected_user.player_id)
    if player_index != len(player_options) - 1:
        save = DB_manager.get_player_save(player_options[player_index])
    else: # create new player
        save = DB_manager.create_player(input("Enter the name of your new player").strip(), starting_bal(lobby_UI_controller, connected_user.player_id))
        
    # user has chosen their player
    connected_user.player_id = save.unique_name
    
    all_games: GameManager = GameManager([connected_user])
    all_games.game_selecter()

    print("saving all active players")
    DB_manager.save_all()


if __name__ == "__main__":
    main()
