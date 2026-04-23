# core/game_utils.py

import random
import pygame
import sys

from core.game_context import GameContext

# --------------------------------------------------
# PLAYER INFO
# --------------------------------------------------

def get_name(ctx: GameContext):
    return ctx.game.player.name


def has_gold(ctx: GameContext, val=0):
    return ctx.game.player.gold >= val and ctx.game.player.gold > 0


def give_gold(ctx: GameContext, val: int):
    if val == -1:
        ctx.game.player.gold = 0
    else:
        ctx.game.player.gold = max(ctx.game.player.gold - val, 0)


def get_gold(ctx: GameContext, val: int):
    ctx.game.player.gold += val


def print_gold(ctx: GameContext):
    return ctx.game.player.gold


def has_item(ctx: GameContext, item: str):
    return item in ctx.game.player.inventory


def get_item(ctx: GameContext, item: str):
    ctx.game.player.inventory.append(item)

def get_move(ctx: GameContext, ability: str):
    ctx.game.player.moves.append(ability)


# --------------------------------------------------
# COMBAT SYSTEM
# --------------------------------------------------

def fight(ctx: GameContext, enemy, new_fight=True, allow_forfeit=False):
    print("\n[Open battle window]")

    ctx.game.restore_window()

    if new_fight:
        ctx.game.battle_prep(enemy, allow_forfeit)
    else:
        ctx.game.ran_away = False
        ctx.game.last_player_action = ""

    while alive(ctx) and enemy_alive(ctx) and not ctx.game.ran_away:
        ctx.game.make_buttons()
        ctx.game.run_battle()

        if ctx.game.ran_away:
            return False

    if not alive(ctx):
        death(ctx)

    return True


def alive(ctx: GameContext):
    return ctx.game.player.is_alive()


def enemy_alive(ctx: GameContext):
    return ctx.game.enemy.is_alive()


def attack_up(ctx: GameContext, val: int):
    ctx.game.player.attack += val


def defense_up(ctx: GameContext, val: int):
    ctx.game.player.defense += val


# --------------------------------------------------
# DICE / CHECKS
# --------------------------------------------------

def check(ctx: GameContext, dc: int, stat: str):
    return random.randint(1, 20) + getattr(ctx.game.player, stat) > dc


# --------------------------------------------------
# HEALING / REST
# --------------------------------------------------

def rest(ctx: GameContext):
    heal_hp(ctx)
    heal_mp(ctx)
    print("Your HP and MP have been restored to full.")
    message = restore_defense(ctx)
    if message:
        print("Your " + message + ".")

def heal_hp(ctx: GameContext, val: int = None):
    if val:
        ctx.game.player.hp = min(ctx.game.player.max_hp, ctx.game.player.hp + val)
    else:
        ctx.game.player.hp = ctx.game.player.max_hp

def heal_mp(ctx: GameContext, val: int = None):
    if val:
        ctx.game.player.mp = min(ctx.game.player.max_mp, ctx.game.player.mp + val)
    else:
        ctx.game.player.mp = ctx.game.player.max_mp

def restore_defense(ctx) -> str:
    if ctx.game.player.defense_mod < 0:
        return ctx.game.player.modify_defense(-ctx.game.player.defense_mod)
    return ""

def cleanse_debuff_statuses(ctx) -> None:
    for status in list(ctx.game.player.statuses):
        if "debuff" in status.tags and "cleansable" in status.tags:
            status.duration = 0
            print(f"{status.name} has been removed.")
            ctx.game.player.remove_status(status.id)
    

# --------------------------------------------------
# PLAYER INITIALIZATION
# --------------------------------------------------

def init_player(ctx: GameContext):
    ctx.game.player.gold = 5
    ctx.game.player.cha = 1

    if ctx.game.player.name == "Bard":
        ctx.game.player.cha += 4

    ctx.game.player.dex = 3
    if ctx.game.player.name == "Rogue":
        ctx.game.player.dex = 6


# --------------------------------------------------
# GAME END STATES
# --------------------------------------------------

def death(ctx: GameContext):
    print("\nYou have died. Your journey is over.")
    input("Press Enter to Quit...")
    shut_down()


def victory(ctx: GameContext):
    print("You finished with", ctx.game.player.gold, "gold. Well done!")
    shut_down()


# --------------------------------------------------
# SHUTDOWN
# --------------------------------------------------

def shut_down():
    pygame.quit()
    sys.exit()