from Deck import Deck
from Player import Player
from Player import BlackJackDealer
from Player import BlackJackPlayer
from Wager import Wager
from util import prompt_yes_or_no

## TODO:
#       - Wager
#           - every player needs to be able to wager
#           - wager should be persistant across each, turn, round, and even different games
#           - maybe players should own wagers?
#       -add statement for when you have zero balance

#       -formating
#           say you stayed or you hit
#           see cards prior to deciding ace
#           don't ask the player about the ace if they get 21

#       - Make another simple game to test our game select system and wagers (maybe war)
#       - figure out how to do multiple players in a game
#           - hands exist in files that players can open
#           - different server processes speaking to main server/game (better if we want to move this logic somewhere else later like a web app, but annoying to implement)
#       - make game interface

class Games:
    def __init__(self, num_players):
        self.num_players =num_players
        self.current_game: Game = None
    
    def game_selecter(self):
        gameType = int(input("What game would you like to play? (select 1 to see list or enter the number of the game is you already know): "))
        while True:
            match gameType:
                case 1:
                    gameType = int(input("1 for repeat list, 2 for Black Jack"))
                case 2:
                    self.current_game = BlackJack(self.num_players)
                    break
        self.current_game.start()

class Game:
    def start(self):
        ## all games are responsible for returning out of this method when completed        
        raise ValueError("THIS IS AN INTERFACE. This method must be overidden")

class Gamble(Game):
    def __init__(self):
        self.wager: Wager = Wager()
        self.wager.starting_Bal()

    def keep_playing(self, wager):
        ans = prompt_yes_or_no("Do you want to play again? ")
        if ans:
            print(f"Your current balance is: {wager}")
            self.start()
        else:
            quit()
            
class BlackJack(Gamble):
    def __init__(self,numPlayers):
        super().__init__()
        self.deck = Deck(['A',2,3,4,5,6,7,8,9,10,'J','Q','K'], ['CLUB','HEART','SPADE','DIAMOND'], {"K": 10, "Q": 10, "J": 10, "A": -1})
        self.deck.shuffle()
        self.numPlayers = numPlayers
        
        self.dealer: BlackJackDealer = BlackJackDealer("Dealer")
        p = BlackJackPlayer(1)
        self.players: list[BlackJackPlayer] = [p]
        self.is_wagering = False

    def start(self):
        if prompt_yes_or_no("Do you want to wager this round?"):
            self.bet = self.wager.wagering()
            self.is_wagering = True
        else:
            self.is_wagering = False

        self.start_round()

    # def keep_playing():
        
    def discard_hands(self):
        for p in self.players:
            p.hand.clear()
        self.dealer.hand.clear()

    def player_turn(self, player: BlackJackPlayer):
        def print_card_info():
            print(f"\n{player}\n")
            
        print_card_info()

        player_points = player.point_checker()

        def print_points():
            print(f"\t{player_points} total\n")
        
        did_hit = True
        while did_hit and player_points <= 21:
            print_points()
            player_points, did_hit = player.hit(self.deck)
            print_card_info()
            print_points()
            if player_points == 21:
                print('Black Jack, you win')
                if self.is_wagering:
                    self.wager.won_bet(self.bet, 1.5)
                    print("Your remaining Balance is: ")
                    print(self.wager.balance)
                self.keep_playing(self.wager.balance)
            elif player_points > 21:
                print("You Lose, Bust")
                if self.is_wagering:
                    self.wager.lost_bet(self.bet)
                    print("Your remaining Balance is: ")
                    print(self.wager.balance)
                self.keep_playing(self.wager.balance)

    def deal_hands(self):
        # 1 face up card to each player, 1 face down card to dealer, 1 face up card to each player, 1 face up card to dealer
        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)

        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)
        print(f"\nThe dealer has drawn.\n\ttop card: {self.dealer.hand.get_top()}")

    def init_game(self):
        id = input("Enter an ID number: ")
        self.players.append(BlackJackPlayer(id))
    
    # def black_jack_checker(self, deck):
    #     if
        
    def start_round(self):
        self.discard_hands()
        self.deal_hands()
        if self.players[0].has_blackjack():
            print('Black Jack, you win')
            if self.is_wagering:
                self.wager.won_bet(self.bet, 1.5)
                print("Your remaining Balance is: ")
                print(self.wager.balance)
            self.keep_playing(self.wager.balance)
        # all player turns
        for player in self.players:
            self.player_turn(player)
                
        # dealer turn
        print(self.dealer)
        dealer_points = self.dealer.point_checker()
        print(f"Dealer current points: {dealer_points}")
        if dealer_points == 21:
            print('Dealer got Black Jack')
            if self.is_wagering:
                self.wager.lost_bet(self.bet)
            self.keep_playing(self.wager.balance)
        if dealer_points > 21:
            print("Dealer Busted")
            if self.is_wagering:
                self.wager.won_bet(self.bet,1)
            self.keep_playing(self.wager.balance)
        
        # did_hit = True
        # while did_hit:
        dealer_points = self.dealer.hit(self.deck)
        player_points = self.players[0].point_checker()

        # end of game
        if player_points > player_points:
            print("Player wins!!")
            if self.is_wagering:
                self.wager.won_bet(self.bet,1)
                print("Your remaining Balance is: ")
                print(self.wager.balance)
            self.keep_playing(self.wager.balance)
        elif player_points < dealer_points:
            print("House wins :(")
            if self.is_wagering:
                self.wager.lost_bet(self.bet)
                print("Your remaining Balance is: ")
                print(self.wager.balance)
            self.keep_playing(self.wager.balance)
        elif player_points == dealer_points:
            print("tie")
            self.keep_playing(self.wager.balance)