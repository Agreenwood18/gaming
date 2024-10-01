from Deck import Deck
from Player import Player
from Player import BlackJackDealer
from Player import BlackJackPlayer
from Bookie import Bookie
from util import print_chunk, prompt_yes_or_no

## TODO:
#       - Wager
#           - every player needs to be able to wager
#           - wager should be persistant across each, turn, round, and even different games
#           - maybe players should own wagers?
#       -add statement for when you have zero balance


#          -terminal
#               option to opt out of certain games before playing

#       design:
#           - where should the A question go? and is it always called?
#           - players can have a print method that handles nicer formatting (\n on both sides, etc)
#               - helps a ton later when we want to do multiple terminals because players will see different output
#           - we can finish this without asking the player at the end if they want to use ace as 11 or 1. We can assume the best hand

#       -formating
#           say you stayed or you hit
#           see cards prior to deciding ace
#           don't ask the player about the ace if they get 21

#       - Make another simple game to test our game select system and wagers (maybe war)
#       - figure out how to do multiple players in a game
#           - hands exist in files that players can open
#           - different server processes speaking to main server/game (better if we want to move this logic somewhere else later like a web app, but annoying to implement)
#       - make game interface

class Game:
    def __init__(self, name) -> None:   
        self.name = name

    def start(self, _player_ids):
        ## all games are responsible for returning out of this method when completed        
        raise ValueError("THIS IS AN INTERFACE. This method must be overidden")

class GambleGame(Game):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.bookie: Bookie = Bookie()

    def keep_playing(self) -> bool:
        # TODO: ask about player their banks?
        return prompt_yes_or_no(f"Do you still want to play {self.name}?")

            
class BlackJack(GambleGame):
    def __init__(self, player_ids) -> None:
        super().__init__("BlackJack")
        self.players: list[BlackJackPlayer] = []
        for id in player_ids:
            self.players.append(BlackJackPlayer(id))

        self.deck = Deck(['A',2,3,4,5,6,7,8,9,10,'J','Q','K'], ['CLUB','HEART','SPADE','DIAMOND'], {"K": 10, "Q": 10, "J": 10, "A": -1})
        self.deck.shuffle()
        
        self.dealer: BlackJackDealer = BlackJackDealer()
       
        self.is_wagering = False

    def start(self):
        while True:
            for p in self.players:
                if prompt_yes_or_no("Do you want to wager this round? "):
                    self.bookie.prompt_wager(p.id)
                    self.is_wagering = True
                else:
                    self.is_wagering = False

            print_chunk("THE ROUND HAS BEGUN!!")

            self.deal_hands()
            self.play_round()

            self.discard_hands()

            if not self.keep_playing():
                break
        

    # def keep_playing():
        
    def discard_hands(self):
        for p in self.players:
            p.hand.clear()
        self.dealer.hand.clear()

    def player_turn(self, player: BlackJackPlayer):
        # OPTIONS:
        #   player drew blackjack
        #   player decides if they should hit no matter what after that (can't get over. even two A would have option to hit)
        #   player is presented with their hand and prompted for a hit


        # def print_card_info():
        #     print(f"\nPlayer ({player})'s {player.hand}\n")
            
        # player_points = player.point_checker()


        
        # TODO: write a blackjack checker method (check 1 or 11 options for A) and break/don't start loop if player has BJ
        did_hit = True
        while player.can_hit() and did_hit:
            print(player)
            did_hit = player.hit(self.deck)
            if did_hit:
                print(f"({player.id}) hit!\n\t drawn card: {player.hand.get_top()}")
        print_chunk()


    def deal_hands(self):
        # 1 face up card to each player, 1 face down card to dealer, 1 face up card to each player, 1 face up card to dealer
        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)

        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)
        print_chunk(f"The dealer has drawn.\n\ttop card: {self.dealer.hand.get_top()}, (hidden)")
        # print("The dealer has drawn their second card\n\t", self.dealer.hand)   
        
    def play_round(self) -> None:
        # all player turns
        for player in self.players:
            self.player_turn(player)
                
        # dealer turn
        dealer_points = self.dealer.hit(self.deck) # hits until done
        print_chunk(f"Dealer Stays\n\thand: {self.dealer.hand}")

        # calculate scores
        for player in self.players:
            # ask the player what val they want their aces to be
            player_points = player.point_checker() 

            print_chunk(f"Round over:\n\t({player.id})'s points: {player_points}\n\tdealer's points: {dealer_points}")

            # end of game
            if player_points == 21:
                print(f"Yea yea... ({player.id}) got a blackjack")
                self.bookie.cashout_win_loss(player.id, True, 1.5)
            elif player_points > 21:
                print(f"({player.id}) busted...")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, False)
            elif dealer_points > 21:
                print(f"({player.id}) got veryyy lucky... dealer busted with a {dealer_points}")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, True, 1)
            elif player_points > dealer_points:
                print(f"({player.id}) wins!!")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, True, 1)
            elif player_points < dealer_points:
                print(f"House beat ({player.id}) :(")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, False)
            elif player_points == dealer_points:
                print(f"Player ({player.id}) tied the dealer")
            else:
                print("what could have possibly happened here???")
                