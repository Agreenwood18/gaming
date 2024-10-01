from DatabaseManager import DatabaseManager
from util import get_int_response

class Bookie():
    def __init__(self) -> None:
        self.player_dict: dict[str, int] = dict() # {player_id: current_bet}

        # grab our own version on the singleton
        self.DB_manager: DatabaseManager = DatabaseManager()
    
    ## mult should only ever be adjusted if has_won==True
    ## NOTE: this removes all "knowledge" of the players interaction with the bookie
    def cashout_win_loss(self, player_id: str, has_won: bool, mult=1) -> None:
        bet: int | None = self.player_dict.get(player_id, None)
        if bet == None:
            # TODO: do something else
            raise ValueError(f"Player {player_id} did not have a bet")

        if not has_won:
            bet *= -1
        
        # NOTE: default arg is mult=1; only affects wins in theory (to recreate previous lost and won logic)
        bet *= mult
        
        self.DB_manager.adjust_money(bet, player_id)   
    
    def prompt_wager(self, player_id: str) -> None:
        bet: int = get_int_response("How much would you like to wager? ")
        bal: int = self.DB_manager.get_player_save(player_id).money
        while bet > bal:
            bet = get_int_response(f"You do not have enough in your balance to wager this amount (you have {bal}). ")
        
        self.player_dict[player_id] = bet

    def __str__(self) -> str:
        return f"bets: {self.player_dict}"