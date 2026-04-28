abilities = {
            "slash": {
                "id": "slash",
                "name": "Slash",
                "effect": ["damage"], 
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense + 5
            },
            "heavy_strike": {
                "id": "heavy_strike",
                "name": "Heavy Strike",
                "effect": ["damage"], 
                "damage": lambda ctx: (ctx.user.attack - ctx.target.defense) * 2 - 3
            },
            "bite": {
                "id": "bite",
                "name": "Bite",
                "effect": ["damage"], 
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense + 2
            },
            "scratch": {
                "id": "scratch",
                "name": "Scratch",
                "effect": ["damage"], 
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense - 2
            },
            "fire_breath": {
                "id": "fire_breath",
                "name": "Fire Breath",
                "effect": ["damage"], 
                "damage": lambda ctx: 25 - ctx.target.defense
            },
            "greater_fire_breath": {
                "id": "greater_fire_breath",
                "name": "Greater Fire Breath",
                "effect": ["damage"], 
                "damage": lambda ctx: 30 - ctx.target.defense
            },
            "surprise": {
                "id": "surprise",
                "name": "Surprise",
                "effect": ["status"], 
                "func": lambda ctx: ctx.game.decrease_stat(ctx.target, "defense", -2)
            },
            "poison_blade": {
                "id": "poison_blade",
                "name": "Poison Blade",
                "effect": ["damage", "status"], 
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense - 5,
                "func": lambda ctx: ctx.game.poison(ctx.target, 5)
            },
            "double_strike": {
                "id": "double_strike",
                "name": "Double Strike",
                "effect": ["damage"],
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense - 2,
                "hits": 2
            },
            "fireball": {
                "id": "fireball",
                "name": "Fireball",
                "effect": ["damage"], 
                "cost": {
                    "mp": 10, 
                },
                "damage": lambda ctx: ctx.user.magic - ctx.target.defense + 5, 
                "hover": "Damage"
            },
            "ice_spike": {
                "id": "ice_spike",
                "name": "Ice Spike",
                "effect": ["damage"], 
                "cost": {
                    "mp": 8, 
                },
                "damage": lambda ctx: ctx.user.magic - ctx.target.defense - 5, 
                "hover": "Damage"
            },
            "lambda": {
                "id": "lambda",
                "name": "Lambda",
                "effect": ["status"], 
                "cost": {
                    "mp": 5, 
                }, 
                "func": lambda ctx: ctx.game.summon_sheep(ctx.user), 
                "hover": "Summon a sheep to defend you"
            },
            "magic_up": {
                "id": "magic_up",
                "name": "Magic Up",
                "effect": ["status"], 
                "cost": {
                    "mp": 20, 
                },
                "func": lambda ctx: ctx.game.increase_stat(ctx.user, "magic", 10), 
                "hover": "+10 Magic"
            },
            "potion": {
                "id": "potion",
                "name": "Potion",
                "effect": ["heal"], 
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.user.restore_hp(30), 
                "hover": "+30 HP",
                "heal": 30
            },
            "super_potion": {
                "id": "super_potion",
                "name": "Super Potion",
                "effect": ["heal"], 
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.user.restore_hp(60), 
                "hover": "+60 HP",
                "heal": 60
            },
            "mana_potion": {
                "id": "mana_potion",
                "name": "Mana Potion",
                "effect": ["status"],
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.user.restore_mp(20), 
                "hover": "+20 MP"
            },
            "power_boost": {
                "id": "power_boost",
                "name": "Power Boost",
                "effect": ["status"],
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.game.increase_stat(ctx.user, "attack", 10), 
                "hover": "+5 Attack"
            },
            "magic_boost": {
                "id": "magic_boost",
                "name": "Magic Boost",
                "effect": ["status"],
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.game.increase_stat(ctx.user, "magic", 10), 
                "hover": "+10 Magic"
            },
            "dragon_bane": {
                "id": "dragon_bane",
                "name": "Dragon's Bane",
                "effect": ["status"],
                "cost": {
                    "item": 1,
                },
                "func": lambda ctx: ctx.game.kill_dragon(ctx), 
                "hover": "Kills a dragon"
            },
            "smoke_bomb": {
                "id": "smoke_bomb",
                "name": "Smoke Bomb",
                "effect": ["status"],
                "cost": {
                    "item": 1,
                },
                "func": lambda ctx: ctx.game.try_escape(100), 
                "hover": "Escapes combat without fail."
            },
            "valor": {
                "id": "valor",
                "name": "Valor",
                "effect": ["status"],
                "func": lambda ctx: ctx.game.valor(ctx.user),
                "hover": "Increases the user's Attack and Defense for 3 turns."
            },
            "rage": {
                "id": "rage",
                "name": "Rage",
                "effect": ["status"],
                "func": lambda ctx: ctx.game.rage(ctx.user),
                "hover": "The user takes half damage for 3 turns."
            },
            "sheepda": {
                "id": "sheepda",
                "name": "Sheepda",
                "effect": ["status"],
                "func": lambda ctx: ctx.game.sheepda(ctx.user),
                "hover": "Summons a flock of sheep to block attacks for three turns."
            },
            "armorup": {
                "id": "armorup",
                "name": "ArmorUp",
                "effect": ["status"],
                "func": lambda ctx: ctx.game.armor_up(ctx.user),
                "hover": "Increases your armor."
            },
            "sleep": {
                "id": "sleep",
                "name": "Sleep",
                "effect": ["status"],
                "func": lambda ctx: ctx.game.sleep(ctx.target),
                "hover": "Puts the enemy to sleep for 3 turns."
            },
            "superior_poison": {
                "id": "superior_poison",
                "name": "Superior Poison",
                "effect": ["status"],
                "func": lambda ctx: ctx.game.poison(ctx.target, 15),
                "hover": "Applies 15 Poison to the enemy."
            },
            "pass": {
                "id": "pass",
                "name": "Pass",
                "effect": ["status"],
                "func": lambda ctx: "It did nothing.",
                "hover": "Pass the turn."
            },
        }