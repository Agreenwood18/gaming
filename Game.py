from Bookie import Bookie
from UIController import UIController

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
    def __init__(self, name: str, UI_controller: UIController) -> None:   
        self.name: str = name
        self.UI_controller: UIController = UI_controller

    def start(self, _player_ids: list[str]) -> None:
        ## all games are responsible for returning out of this method when completed        
        raise ValueError("THIS IS AN INTERFACE. This method must be overidden")

class GambleGame(Game):
    def __init__(self, name: str, UI_controller: UIController) -> None:
        super().__init__(name, UI_controller)
        self.bookie: Bookie = Bookie()

    def keep_playing(self) -> bool:
        # TODO: ask about player their banks?
        return self.UI_controller.prompt_yes_or_no(f"Do you still want to play {self.name}?", "TODO: this will be different... with multiplayer!")
