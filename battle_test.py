import sys
import pygame

from core.advanced_rpg import BattleGame
from core.character_select_screen import CharacterSelectScreen
from core.game_context import GameContext

if __name__ == "__main__":
    # Create game context
    ctx = GameContext()

    # Character select (pygame)
    selector = CharacterSelectScreen()
    player = selector.run()

    # Store player
    ctx.player = player

    # Create battle system
    game = BattleGame(player, ctx)
    ctx.game = game

    # Start a test battle
    game.battle_prep("Black Dragon", debug=True)
    game.make_buttons()
    game.run_battle()
    pygame.quit()
    sys.exit()