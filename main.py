# main.py

import advanced_rpg

from areas.coliseum import coliseum_path
from core.game_utils import get_gold, init_player
from core.map_engine import (
    randomize_areas,
    main as run_map,
)
from core.game_context import GameContext


# --------------------------------------------------
# PROGRAM ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":

    # Create battle system
    game = advanced_rpg.BattleGame()
    ctx = GameContext(game)

    # CHARACTER SELECT
    game.run_character_select()

    # give player to RPG system
    init_player(ctx)
    
    # now start branching RPG
    randomize_areas(ctx)
    run_map(ctx)