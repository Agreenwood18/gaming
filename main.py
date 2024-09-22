from Games import Games
from Player import Player
from Bank import Bank
from util import get_int_response

import Global

def main():
    Global.bank = Bank()

    player_ids = []
    for n in range(1, get_int_response("How many people are playing? ") + 1):
        Global.bank.starting_Bal(n)
        player_ids.append(n)

    all_games = Games(player_ids)
    all_games.game_selecter()

if __name__ == "__main__":
    main()
