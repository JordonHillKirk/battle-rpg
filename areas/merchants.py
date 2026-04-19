# areas/merchants.py

import random

from core.area_utils import forward, press_enter_to_continue
from core.game_context import GameContext
from core.game_utils import (
    get_gold,
    get_move,
    has_gold,
    give_gold,
    get_item,
    has_item,
    print_gold,
)


# --------------------------------------------------
# TRAVELING MERCHANT (PHYSICAL ITEMS)
# --------------------------------------------------

def traveling_merchant(ctx, kwargs):
    while True:
        print("\nYou spot a traveling merchant on the side of the path.")
        print("They say they have helpful goods to sell.")
        print("Do you stop to browse their wares?")
        print("1. Yes, stop to browse.")
        print("2. No, keep moving on.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            return shop(
                ctx,
                {"id": "potion", "price": 5, "on_buy": lambda ctx: get_item(ctx, "potion")},
                {"id": "power_boost", "price": 10, "on_buy": lambda ctx: get_item(ctx, "power_boost")},
                {"id": "dragon_bane", "price": 30, "on_buy": lambda ctx: get_item(ctx, "dragon_bane")}
            )

        elif choice == "2":
            print("You keep going.")
            return forward()

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# TRAVELING MERCHANT (MAGIC ITEMS)
# --------------------------------------------------

def traveling_merchant2(ctx: GameContext, kwargs):
    while True:
        print("\nYou spot a traveling merchant on the side of the path.")
        print("They say they have helpful goods to sell.")
        print("Do you stop to browse their wares?")
        print("1. Yes, stop to browse.")
        print("2. No, keep moving on.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            return shop(
                ctx, 
                {"id": "mana_potion", "price": 5, "on_buy": lambda ctx: get_item(ctx, "mana_potion")},
                {"id": "magic_boost", "price": 10, "on_buy": lambda ctx: get_item(ctx, "magic_boost")},
                {"id": "dragon_bane", "price": 30, "on_buy": lambda ctx: get_item(ctx, "dragon_bane")}
            )

        elif choice == "2":
            print("You keep going.")
            return forward()

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# TRAVELING MERCHANT (STATUS RESTORATION ITEMS)
# --------------------------------------------------

def traveling_merchant3(ctx: GameContext, kwargs):
    while True:
        print("\nYou spot a traveling merchant on the side of the path.")
        print("They say they have helpful goods to sell.")
        print("Do you stop to browse their wares?")
        print("1. Yes, stop to browse.")
        print("2. No, keep moving on.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            return shop(
                ctx, 
                {"id": "antidote", "price": 5, "on_buy": lambda ctx: get_item(ctx, "antidote")},
                {"id": "burn_heal", "price": 5, "on_buy": lambda ctx: get_item(ctx, "burn_heal")},
                {"id": "dragon_bane", "price": 30, "on_buy": lambda ctx: get_item(ctx, "dragon_bane")}
            )

        elif choice == "2":
            print("You keep going.")
            return forward()

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# TRAVELING MERCHANT (ABILITIES)
# --------------------------------------------------

def traveling_merchant4(ctx: GameContext, kwargs):
    while True:
        print("\nYou spot a traveling merchant on the side of the path.")
        print("They say they have helpful goods to sell.")
        print("Do you stop to browse their wares?")
        print("1. Yes, stop to browse.")
        print("2. No, keep moving on.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            abilities = ctx.game.abilities
            options = []
            for key in list(abilities.keys()):
                if abilities[key].get("cost", {}).get("mp", None) or abilities[key].get("cost", {}).get("item", None):
                    continue
                if key in ctx.game.player.moves:
                    continue
                options.append(key)

            choices = random.sample(options, 3)

            return shop(
                ctx, 
                # {"id": choices[0], "price": 20, "on_buy": lambda ctx: get_move(ctx, choices[0])},
                # {"id": choices[1], "price": 20, "on_buy": lambda ctx: get_move(ctx, choices[1])},
                # {"id": choices[2], "price": 20, "on_buy": lambda ctx: get_move(ctx, choices[2])}
                {"id": "poison_blade", "price": 20, "on_buy": lambda ctx: get_move(ctx, "poison_blade")},
                {"id": "armorup", "price": 20, "on_buy": lambda ctx: get_move(ctx, "armorup")},
                {"id": "sheepda", "price": 20, "on_buy": lambda ctx: get_move(ctx, "sheepda")}
            )

        elif choice == "2":
            print("You keep going.")
            return forward()

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# SHOP SYSTEM
# --------------------------------------------------

def shop(ctx, *items):
    while True:
        print(f"\nYou have {print_gold(ctx)} gold.")
        print("The following items are available for purchase:")

        # Build list of purchasable items
        available_items = []

        for entry in items:
            item_id = entry["id"]
            price = entry["price"]

            # Prevent duplicate Dragon's Bane
            if item_id == "dragon_bane" and has_item(ctx, item_id):
                continue

            ability = ctx.game.get_ability(item_id)
            available_items.append((entry, ability, price))

        # Display items
        for i, (entry, ability, price) in enumerate(available_items, 1):
            print(
                f"{i}. {ability['name']} ({price} gold)"
                f"{'' if has_gold(ctx, price) else ' [Not enough gold]'}"
            )

        print(f"{len(available_items)+1}. Buy nothing")

        choice = input(f"What do you buy? (1-{len(available_items)+1}): ")
        print()

        # Leave shop
        if choice == str(len(available_items) + 1):
            print("You say goodbye to the merchant, and move on.")
            return forward()

        elif choice == "test":
            get_gold(ctx, 20)

        # Purchase item
        elif choice.isnumeric() and 1 <= int(choice) <= len(available_items):

            entry, ability, price = available_items[int(choice) - 1]

            if has_gold(ctx, price):
                name = ability["name"]
                article = "an" if len(name) > 0 and name[0].lower() in "aeiou" else "a"

                print(f"You buy {article} {name}.")
                print(f"[You spent {price} gold]")
                print(f"[You gained {article} {name}]")

                give_gold(ctx, price)
                purchase(ctx, entry)

            else:
                print("You do not have enough gold for that item.")

        else:
            print("Not a valid choice. Try again.")

        press_enter_to_continue()

def purchase(ctx, entry):
    entry["on_buy"](ctx)