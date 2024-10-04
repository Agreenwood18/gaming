from BlackjackPlayers import BlackjackDealer, BlackjackPlayer
from Deck import Deck
from Game import GambleGame


class BlackjackGame(GambleGame):
    def __init__(self, player_ids, UI_controller) -> None:
        super().__init__("BlackJack", UI_controller)
        self.players: list[BlackjackPlayer] = []
        for id in player_ids:
            self.players.append(BlackjackPlayer(id))

        self.deck = Deck(['A',2,3,4,5,6,7,8,9,10,'J','Q','K'], ['CLUB','HEART','SPADE','DIAMOND'], {"K": 10, "Q": 10, "J": 10, "A": -1})
        self.deck.shuffle()
        
        self.dealer: BlackjackDealer = BlackjackDealer()
       
        self.is_wagering = False

    def start(self) -> None:
        while True:
            for p in self.players:
                if self.UI_controller.prompt_yes_or_no("Do you want to wager this round? ", p.id):
                    self.bookie.prompt_wager(p.id, self.UI_controller)
                    self.is_wagering = True
                else:
                    self.is_wagering = False

            self.UI_controller.broadcast_to_all("THE ROUND HAS BEGUN!!")

            self.deal_hands()
            self.play_round()

            self.discard_hands()

            if not self.keep_playing():
                break
        
    def discard_hands(self) -> None:
        for p in self.players:
            p.hand.clear()
        self.dealer.hand.clear()

    def player_turn(self, player: BlackjackPlayer) -> None:
        # TODO: write a blackjack checker method (check 1 or 11 options for A) and break/don't start loop if player has BJ
        did_hit = True
        while player.can_hit() and did_hit:
            self.UI_controller.whisper_this_to(f"Here are your {len(player.hand)} cards: {player.hand}", player.id)
            did_hit = player.hit(self.deck, self.UI_controller)
            if did_hit:
                self.UI_controller.broadcast_to_all(f"{player} hit!\n\t drawn card: {player.hand.get_top()}")

    def deal_hands(self) -> None:
        # 1 face up card to each player, 1 face down card to dealer, 1 face up card to each player, 1 face up card to dealer
        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)

        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)
        self.UI_controller.broadcast_to_all(f"The dealer has drawn.\n\ttop card: {self.dealer.hand.get_top()}, (hidden)")
        
    def play_round(self) -> None:
        # all player turns
        for player in self.players:
            self.player_turn(player)
                
        # dealer turn
        dealer_points = self.dealer.hit(self.deck) # hits until done
        self.UI_controller.broadcast_to_all(f"Dealer Stays\n\thand: {self.dealer.hand}")

        # calculate scores
        for player in self.players:
            # ask the player what val they want their aces to be
            player_points = player.get_score() 

            self.UI_controller.broadcast_to_all(f"Round over:\n\t{player}'s points: {player_points}\n\tdealer's points: {dealer_points}")

            # TODO: after multiplayer, actually send individualized messages
            # end of game
            if player_points == 21:
                self.UI_controller.whisper_this_to(f"Yea yea... you got a blackjack", player.id)
                # print(f"Yea yea... {player} got a blackjack")
                self.bookie.cashout_win_loss(player.id, True, 1.5)
            elif player_points > 21:
                self.UI_controller.whisper_this_to(f"You busted...", player.id)
                # print(f"{player} busted...")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, False)
            elif dealer_points > 21:
                self.UI_controller.whisper_this_to(f"You got veryyy lucky... dealer busted with a {dealer_points}", player.id)
                # print(f"{player} got veryyy lucky... dealer busted with a {dealer_points}")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, True, 1)
            elif player_points > dealer_points:
                self.UI_controller.whisper_this_to(f"You win!!", player.id)
                # print(f"{player} wins!!")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, True, 1)
            elif player_points < dealer_points:
                self.UI_controller.whisper_this_to(f"House beat you :(", player.id)
                # print(f"House beat {player} :(")
                if self.is_wagering:
                    self.bookie.cashout_win_loss(player.id, False)
            elif player_points == dealer_points:
                self.UI_controller.whisper_this_to(f"You tied the dealer", player.id)
                # print(f"Player {player} tied the dealer")
            else:
                print("what could have possibly happened here???") # TODO: debug logging