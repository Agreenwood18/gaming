from BlackjackPlayers import BlackjackDealer, BlackjackPlayer
from Deck import Deck
from Game import GambleGame
from UIController import Message


class BlackjackGame(GambleGame):
    def __init__(self, player_ids, UI_controller) -> None:
        super().__init__("BlackJack", UI_controller)
        self.players: list[BlackjackPlayer] = []
        for id in player_ids:
            self.players.append(BlackjackPlayer(id))

        self.deck = Deck(['A',2,3,4,5,6,7,8,9,10,'J','Q','K'], ['CLUB','HEART','SPADE','DIAMOND'], {"K": 10, "Q": 10, "J": 10, "A": -1})
        self.deck.shuffle()

        self.dealer: BlackjackDealer = BlackjackDealer()
        self.results: dict[str, int] = dict()


    def start(self) -> None:
        while True:
            
            ids = [p.id for p in self.players]
            responses =  self.UI_controller.send(Message("Do you want to wager this round?").whisper_to(ids).waitfor_yes_no())
            yes_ids = [key for key, value in responses.items() if value == True]
            self.bookie.prompt_wager(yes_ids)

            self.UI_controller.delay_next(0).send(Message("THE ROUND HAS BEGUN!!"))

            self.deal_hands()
            self.play_round()

            self.discard_hands()

            if not self.keep_playing():
                break
        
    def discard_hands(self) -> None:
        for p in self.players:
            p.hand.clear()
        self.dealer.hand.clear()

    def get_score_string(self, score: int) -> str:
        return f"busted with a {score}" if score > 21 else "got blackjack!" if score == 21 else f"got {score}"

    def player_turn(self, player: BlackjackPlayer) -> None:
        did_hit = True
        while player.can_hit() and did_hit:
            self.UI_controller.send(Message(f"Here is your hand: {player.hand}").whisper_to(player.id))
            did_hit = player.hit(self.deck, self.UI_controller)
            if did_hit:
                self.UI_controller.send(Message(f"{player} hit!\n\t their new hand: {player.hand}"))

        score = player.get_score()
        self.results[player.id] = score
        result_str = self.get_score_string(score)
        self.UI_controller.send(Message(f"You {result_str}!"))
        self.UI_controller.send(Message(f"{player} {result_str}!").exclude(player.id))

    def deal_hands(self) -> None:
        # 1 face up card to each player, 1 face down card to dealer, 1 face up card to each player, 1 face up card to dealer
        for player in self.players:
            player.draw(self.deck)

        self.dealer.draw(self.deck)

        for player in self.players:
            player.draw(self.deck)

        hands = "\n\t".join([f"{p}'s hand: {p.hand}" for p in self.players])
        self.UI_controller.send(Message(f"The dealer has dealt your hands:\n\n\t{hands}"))

        self.dealer.draw(self.deck)
        self.UI_controller.send(Message(f"This is the dealer's hand.\n\ttop card: {self.dealer.hand.get_top()}, (hidden)"))
        
    def play_round(self) -> None:
        # all player turns
        for player in self.players:
            self.player_turn(player)
                
        # dealer turn
        dealer_points = self.dealer.hit(self.deck) # hits until done
        result_str = self.get_score_string(dealer_points)
        draw_num = len(self.dealer.hand) - 2
        self.UI_controller.send(Message(f"The dealer hit {draw_num} time{'s' if draw_num!=1 else ''}, he {result_str}\n\thand: {self.dealer.hand}"))

        # calculate scores
        for player in self.players:
            player_points = self.results[player.id]

            # end of game
            if player_points == 21:
                self.UI_controller.send(Message(f"Yea yea... you got a blackjack").whisper_to(player.id))
                self.bookie.cashout_win_loss(player.id, True, 1.5)
            elif player_points > 21:
                self.UI_controller.send(Message(f"You busted...").whisper_to(player.id))
                self.bookie.cashout_win_loss(player.id, False)
            elif dealer_points > 21:
                self.UI_controller.send(Message(f"You got veryyy lucky... dealer busted with a {dealer_points}! He could have beat you").whisper_to(player.id))
                self.bookie.cashout_win_loss(player.id, True, 1)
            elif player_points > dealer_points:
                self.UI_controller.send(Message(f"You win!!").whisper_to(player.id))
                self.bookie.cashout_win_loss(player.id, True, 1)
            elif player_points < dealer_points:
                self.UI_controller.send(Message(f"House beat you :(").whisper_to(player.id))
                self.bookie.cashout_win_loss(player.id, False)
            elif player_points == dealer_points:
                self.UI_controller.send(Message(f"You tied the dealer").whisper_to(player.id))
            else:
                print("what could have possibly happened here???") # TODO: debug logging
