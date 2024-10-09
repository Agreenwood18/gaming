from DatabaseManager import DatabaseManager
from UIController import Message, UIController

class Bookie():
    def __init__(self, UI_controller: UIController) -> None:
        self.player_dict: dict[str, int] = dict() # {player_id: current_bet}
        self.UI_controller: UIController = UI_controller

        # grab our own version on the singleton
        self.DB_manager: DatabaseManager = DatabaseManager()
    
    ## mult should only ever be adjusted if has_won==True
    ## NOTE: this removes all "knowledge" of the players interaction with the bookie
    def cashout_win_loss(self, player_id: str, has_won: bool, mult=1) -> None:
        bet: int | None = self.player_dict.get(player_id, None)
        if bet == None:
            return
            # raise ValueError(f"Player {player_id} did not have a bet")

        if not has_won:
            bet *= -1
        
        # NOTE: technically you should only change mult from 1 on a win... but maybe not?
        bet *= mult
        
        new_money: int = self.DB_manager.adjust_money(bet, player_id)
        msg: str = (f"You won ${bet}!" if has_won else f"You just lost ${abs(bet)}...") + f" Your new balance is ${new_money}."
        self.UI_controller.send(Message(msg).whisper_to(player_id))
    
    def prompt_wager(self, player_ids: list[str]) -> None:
        msgs: list[Message] = []
        for player_id in player_ids:
            bal = self.DB_manager.get_player_save(player_id).money
            msgs.append(Message(f"How much would you like to wager? (you have ${bal})").whisper_to(player_id).waitfor_int(range_inclusive=(0, bal)))
        msgs.append(Message("The gambling addicts are speaking with their bookie... please wait").exclude(player_ids))

        bets = self.UI_controller.send(msgs)
        for player_id, bet in bets.items():

            self.player_dict[player_id] = bet

    def __str__(self) -> str:
        return f"bets: {self.player_dict}"
