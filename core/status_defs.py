import random

from core.constants import *
from core.status import Status

def get_status_defs(game):
    return {
            "stats_up": lambda: Status(
                "stats_up",
                "Stats Up",
                1,
                {},
                {
                    ATTACK: 0,
                    DEFENSE: 0,
                    MAGIC: 0,
                },
                {BUFF}
            ),
            "stats_down": lambda: Status(
                "stats_down",
                "Stats Down",
                1,
                {
                    ON_BATTLE_END: game.tick_status
                },
                {
                    ATTACK: 0,
                    DEFENSE: 0,
                    MAGIC: 0,
                },
                {DEBUFF, CLEANSABLE}
            ),
            "burn": lambda duration = 5: Status(
                "burn",
                "Burn",
                duration,
                {
                    ON_TURN_END: game.burn_tick,
                    ON_0_DURATION: lambda ctx, status: game.log(f"{ctx.user.pronouns['possessive']} burn faded."),
                },
                {
                    "display_text": "Burn"
                },
                {DEBUFF, CLEANSABLE}

            ),
            "poison": lambda duration = 5: Status(
                "poison",
                "Poison",
                duration,
                {
                    ON_TURN_START: game.poison_tick,
                    ON_0_DURATION: lambda ctx, status: game.log(f"{ctx.user.pronouns['possessive']} poison faded."),
                },
                {
                    "display_text": "Poison"
                },
                {DEBUFF, CLEANSABLE}

            ),
            "rage": lambda duration = 3: Status(
                "rage",
                "Rage",
                duration,
                {
                    ON_TURN_START: game.tick_status,
                    ON_PRE_DAMAGE: game.rage_pre_damage,
                    ON_0_DURATION: lambda ctx, status: game.log(f"{ctx.user.name} calmed down!")
                },
                {
                    "display_text": "Rage"
                },
                {BUFF}
            ),
            "sheep": lambda duration = 0: Status(
                "sheep",
                "Sheep",
                duration or random.randint(1, 2),
                {
                    ON_PRE_DAMAGE: game.sheep_pre_damage,
                    ON_0_DURATION: lambda ctx, status: game.log("    The sheep disappeared.")
                },
                {
                    "display_text": "Sheep",
                    "first_sheep": True
                },
                {BUFF}
            ),
            "sheepda": lambda duration = 3: Status(
                "sheepda",
                "Sheepda",
                duration,
                {
                    ON_TURN_START: game.tick_status,
                    ON_PRE_DAMAGE: game.sheep_pre_damage,
                    ON_0_DURATION: lambda ctx, status: game.log(f"{ctx.user.pronouns['possessive']} sheep disappeared.")
                },
                {
                    "display_text": "Sheepda",
                    "first_sheep": True
                },
                {BUFF}
            ),
            "sleep": lambda duration = 3: Status(
                "sleep",
                "Sleep",
                duration,
                {
                    ON_TURN_START: game.sleep_turn_start,
                    ON_POST_DAMAGE: game.sleep_post_damage,
                    ON_0_DURATION: lambda ctx, status: game.log(f"    {ctx.user.name} woke up!")
                },
                {
                    "display_text": "Asleep",
                },
                {DEBUFF, CLEANSABLE}
            ),
            "speedy_mp_recovery": lambda duration = -1: Status(
                "speedy_mp_recovery",
                "Speedy MP Recovery",
                duration,
                {
                    ON_TURN_START: game.speedy_regen_mp_tick
                },
                {
                    "mp_gain": 1
                },
                {BUFF, PERMANENT}
            ),
            "valor": lambda duration = 3: Status(
                "valor",
                "Valor",
                duration,
                {
                    ON_TURN_START: game.tick_status,
                    ON_0_DURATION: lambda ctx, status: game.log(f"{ctx.user.name}'s Valor wore off.")
                },
                {
                    "display_text": "Valor",
                    ATTACK: 10,
                    DEFENSE: 10
                },
                {BUFF}
            ),
        }