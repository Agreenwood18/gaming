from Blackjack.BlackJackPlayers import BlackJackDealer, BlackJackPlayer
from Deck import Deck
from Game import GambleGame
from util import print_chunk, prompt_yes_or_no


class BlackJack(GambleGame):
    def __init__(self, player_ids, UI_controller) -> None:
        super().__init__("BlackJack", UI_controller)
        self.players: list[BlackJackPlayer] = []
        for id in player_ids:
            self.players.append(BlackJackPlayer(id))

        self.deck = Deck(['A',2,3,4,5,6,7,8,9,10,'J','Q','K'], ['CLUB','HEART','SPADE','DIAMOND'], {"K": 10, "Q": 10, "J": 10, "A": -1})
        self.deck.shuffle()
        
        self.dealer: BlackJackDealer = BlackJackDealer()
       
        self.is_wagering = False

    def start(self) -> None:
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
        
    def discard_hands(self) -> None:
        for p in self.players:
            p.hand.clear()
        self.dealer.hand.clear()

    def player_turn(self, player: BlackJackPlayer) -> None:
       
        # TODO: write a blackjack checker method (check 1 or 11 options for A) and break/don't start loop if player has BJ
        did_hit = True
        while player.can_hit() and did_hit:
            self.UI_controller.whisper_this_to(player, player.id)
            did_hit = player.hit(self.deck)
            if did_hit:
                self.UI_controller.broadcast_to_all(f"({player.id}) hit!\n\t drawn card: {player.hand.get_top()}")
        print_chunk()


    def deal_hands(self) -> None:
        # 1 face up card to each player, 1 face down card to dealer, 1 face up card to each player, 1 face up card to dealer
        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)

        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)
        print_chunk(f"The dealer has drawn.\n\ttop card: {self.dealer.hand.get_top()}, (hidden)")
        
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
            player_points = player.get_score() 

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