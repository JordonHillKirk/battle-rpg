from core.constants import *

def get_abilities():
    return {
        # --------------------------------------------------
        # Attacks
        # --------------------------------------------------
        "slash": {
            ID: "slash",
            NAME: "Slash",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: ctx.user.attack - ctx.target.defense + 5
        },
        "heavy_strike": {
            ID: "heavy_strike",
            NAME: "Heavy Strike",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: (ctx.user.attack - ctx.target.defense) * 2 - 3
        },
        "bite": {
            ID: "bite",
            NAME: "Bite",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: ctx.user.attack - ctx.target.defense + 2
        },
        "scratch": {
            ID: "scratch",
            NAME: "Scratch",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: ctx.user.attack - ctx.target.defense - 2
        },
        "fire_breath": {
            ID: "fire_breath",
            NAME: "Fire Breath",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: 25 - ctx.target.defense
        },
        "poison_breath": {
            ID: "poison_breath",
            NAME: "Poison Breath",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: 20 - ctx.target.defense,
            FUNC: lambda ctx: ctx.game.poison(ctx.target, 3)
        },
        "greater_fire_breath": {
            ID: "greater_fire_breath",
            NAME: "Greater Fire Breath",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: 30 - ctx.target.defense
        },
        "surprise": {
            ID: "surprise",
            NAME: "Surprise",
            TYPE: TYPE_ATTACK,
            FUNC: lambda ctx: ctx.game.decrease_stat(ctx.target, "defense", -2)
        },
        "poison_blade": {
            ID: "poison_blade",
            NAME: "Poison Blade",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: ctx.user.attack - ctx.target.defense - 5,
            FUNC: lambda ctx: ctx.game.poison(ctx.target, 5)
        },
        "double_strike": {
            ID: "double_strike",
            NAME: "Double Strike",
            TYPE: TYPE_ATTACK,
            DAMAGE: lambda ctx: ctx.user.attack - ctx.target.defense - 2,
            HITS: 2
        },
        "steal_item": {
            ID: "steal_item",
            NAME: "Steal Item",
            TYPE: TYPE_ATTACK,
            FUNC: lambda ctx: ctx.game.steal_item(ctx)
        },
        # --------------------------------------------------
        # Spells
        # --------------------------------------------------
        "fireball": {
            ID: "fireball",
            NAME: "Fireball",
            TYPE: TYPE_SPELL,
            COST: {
                COST_MP: 10, 
            },
            DAMAGE: lambda ctx: ctx.user.magic - ctx.target.defense + 5, 
            HOVER: "damage"
        },
        "ice_spike": {
            ID: "ice_spike",
            NAME: "Ice Spike",
            TYPE: TYPE_SPELL,
            COST: {
                COST_MP: 8, 
            },
            DAMAGE: lambda ctx: ctx.user.magic - ctx.target.defense - 5, 
            HOVER: "damage"
        },
        "lambda": {
            ID: "lambda",
            NAME: "Lambda",
            TYPE: TYPE_SPELL,
            COST: {
                COST_MP: 5, 
            }, 
            FUNC: lambda ctx: ctx.game.summon_sheep(ctx.user), 
            HOVER: "Summon a sheep to defend you"
        },
        "magic_up": {
            ID: "magic_up",
            NAME: "Magic Up",
            TYPE: TYPE_SPELL,
            COST: {
                COST_MP: 20, 
            },
            FUNC: lambda ctx: ctx.game.increase_stat(ctx.user, "magic", 10), 
            HOVER: "+10 Magic"
        },
        # --------------------------------------------------
        # Items
        # --------------------------------------------------
        "potion": {
            ID: "potion",
            NAME: "Potion",
            TYPE: TYPE_ITEM,
            COST: {
                COST_ITEM: 1, 
            },
            HEAL: 30,
            FUNC: lambda ctx: ctx.user.restore_hp(30), 
            HOVER: "+30 HP",
        },
        "super_potion": {
            ID: "super_potion",
            NAME: "Super Potion",
            TYPE: TYPE_ITEM,
            COST: {
                "item": 1, 
            },
            HEAL: 60,
            FUNC: lambda ctx: ctx.user.restore_hp(60), 
            HOVER: "+60 HP",
        },
        "mana_potion": {
            ID: "mana_potion",
            NAME: "Mana Potion",
            TYPE: TYPE_ITEM,
            COST: {
                "item": 1, 
            },
            FUNC: lambda ctx: ctx.user.restore_mp(20), 
            HOVER: "+20 MP"
        },
        "power_boost": {
            ID: "power_boost",
            NAME: "Power Boost",
            TYPE: TYPE_ITEM,
            COST: {
                "item": 1, 
            },
            FUNC: lambda ctx: ctx.game.increase_stat(ctx.user, "attack", 10), 
            HOVER: "+5 Attack"
        },
        "magic_boost": {
            ID: "magic_boost",
            NAME: "Magic Boost",
            TYPE: TYPE_ITEM,
            COST: {
                "item": 1, 
            },
            FUNC: lambda ctx: ctx.game.increase_stat(ctx.user, "magic", 10), 
            HOVER: "+10 Magic"
        },
        "dragon_bane": {
            ID: "dragon_bane",
            NAME: "Dragon's Bane",
            TYPE: TYPE_ITEM,
            COST: {
                "item": 1,
            },
            FUNC: lambda ctx: ctx.game.kill_dragon(ctx), 
            HOVER: "Kills a dragon"
        },
        "smoke_bomb": {
            ID: "smoke_bomb",
            NAME: "Smoke Bomb",
            TYPE: TYPE_ITEM,
            COST: {
                "item": 1,
            },
            FUNC: lambda ctx: ctx.game.try_escape(100), 
            HOVER: "Escapes combat without fail."
        },
        # --------------------------------------------------
        # Specials
        # --------------------------------------------------
        "valor": {
            ID: "valor",
            NAME: "Valor",
            TYPE: TYPE_SPECIAL,
            FUNC: lambda ctx: ctx.game.valor(ctx.user),
            HOVER: "Increases the user's Attack and Defense for 3 turns."
        },
        "rage": {
            ID: "rage",
            NAME: "Rage",
            TYPE: TYPE_SPECIAL,
            FUNC: lambda ctx: ctx.game.rage(ctx.user),
            HOVER: "The user takes half damage for 3 turns."
        },
        "sheepda": {
            ID: "sheepda",
            NAME: "Sheepda",
            TYPE: TYPE_SPECIAL,
            FUNC: lambda ctx: ctx.game.sheepda(ctx.user),
            HOVER: "Summons a flock of sheep to block attacks for three turns."
        },
        "armorup": {
            ID: "armorup",
            NAME: "ArmorUp",
            TYPE: TYPE_SPECIAL,
            FUNC: lambda ctx: ctx.game.armor_up(ctx.user),
            HOVER: "Increases your armor."
        },
        "sleep": {
            ID: "sleep",
            NAME: "Sleep",
            TYPE: TYPE_SPECIAL,
            FUNC: lambda ctx: ctx.game.sleep(ctx.target),
            HOVER: "Puts the enemy to sleep for 3 turns."
        },
        "superior_poison": {
            ID: "superior_poison",
            NAME: "Superior Poison",
            TYPE: TYPE_SPECIAL,
            FUNC: lambda ctx: ctx.game.poison(ctx.target, 15),
            HOVER: "Applies 15 Poison to the enemy."
        },



        "pass": {
            ID: "pass",
            NAME: "Pass",
            TYPE: TYPE_ATTACK,
            FUNC: lambda ctx: "It did nothing.",
            HOVER: "Pass the turn."
        },
    }