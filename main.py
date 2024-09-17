from Games import BlackJack
from Games import Games
from Player import Player
from Player import BlackJackPlayer
from Player import BlackJackDealer
from Deck import Deck
from Wager import Wager

def main():
    player_num = int(input("How many people are playing: "))
    all_games = Games(player_num)
    all_games.game_selecter()

if __name__ == "__main__":
    main()

