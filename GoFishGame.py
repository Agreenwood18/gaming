from Deck import Deck
from GoFishPlayer import GoFishPlayer
from Game import Game
from MultiDeckPlayer import MultiDeckPlayer
from UIController import UIController


#TODO: makes the official rules work (4 of a kind)


class GoFishGame(Game):
    def __init__(self, player_ids, UI_controller: UIController) -> None:
        super().__init__("Go Fish", UI_controller)
        self.players: list[MultiDeckPlayer] = []
        for id in player_ids:
            self.players.append(MultiDeckPlayer(id))

        self.deck = Deck(['A',2,3,4,5,6,7,8,9,10,'J','Q','K'], ['CLUB','HEART','SPADE','DIAMOND'], {"K": 10, "Q": 10, "J": 10, "A": -1})
        self.deck.shuffle()

    def start(self) -> None: #_player_ids: list[str])
        self.UI_controller.broadcast_to_all("THE Game HAS BEGUN!!")
        self.deal_hands()
        

        while not(self.end_game()):
            self.play_round()
        else:
            self.finished()



    def end_game(self)-> bool:
        len(self.deck) != 0

    def deal_hands(self):
        x=0
        while x!=7:
            for player in self.players:
                player.draw(self.deck)
            x+=1
    def play_round(self):
        for player in self.players:
            self.player_turn(player)
    
    def player_turn(self,player:MultiDeckPlayer) ->None:
        pairsInHand = player.hand.pair_search()
        self.UI_controller.whisper_this_to(f"YOUR TURN!!!! \t\n")
        self.UI_controller.whisper_this_to(f"Here are your {len(player.hand)} cards: {player.hand}", player.id)
        self.UI_controller.whisper_this_to(f"You have {int(len(pairsInHand))/2} pairs in your hand.", player.id)
        if len(pairsInHand)>0:
            self.UI_controller.whisper_this_to(f"The first instance of the pair will be removed and added to your victory pile")
            MultiDeckPlayer.decks[0].appened(player.hand.remove(pairsInHand.pop()))
            MultiDeckPlayer.decks[0].appened(player.hand.remove(pairsInHand.pop()))
        self.UI_controller.whisper_this_to(f"You now have {len(player.hand)} cards remaining: {player.hand}", player.id)
        self.UI_controller.select_from_list(f"Who would you like to ask:",self.players,player.id)
        
        quit()
        


