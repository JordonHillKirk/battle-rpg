import core.advanced_rpg as advanced_rpg

from core.game_utils import init_player
from core.map_engine import (
    randomize_areas,
    main as run_map,
)
from core.game_context import GameContext
from core.character_select_screen import CharacterSelectScreen


if __name__ == "__main__":

    # 1. Create game context FIRST (no battle yet)
    ctx = GameContext()

    # 2. Character select (pygame)
    selector = CharacterSelectScreen()
    player = selector.run()

    # 3. Store player in context
    ctx.player = player

    # 4. Initialize player (your existing logic)
    init_player(ctx)

    # 5. Create battle system WITH player
    game = advanced_rpg.BattleGame(player, ctx)

    # 6. Attach battle system to context
    ctx.game = game

    # 7. Run map system
    randomize_areas(ctx)
    run_map(ctx)