# areas/merchants.py

from core.area_utils import forward, press_enter_to_continue
from core.game_context import GameContext
from core.game_utils import (
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
                ("potion", 5),
                ("power_boost", 10),
                ("dragon_bane", 30),
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
                ("mana_potion", 5),
                ("magic_boost", 10),
                ("dragon_bane", 30),
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

        for item_id, value in items:

            # Prevent duplicate Dragon's Bane
            if item_id == "dragon_bane" and has_item(ctx, "dragon_bane"):
                continue
            
            item = ctx.game.get_ability(item_id)
            available_items.append((item, value))

        # Display items
        for i, (item, value) in enumerate(available_items, 1):
            print(
                f"{i}. {item["name"]} ({value} gold)"
                f"{'' if has_gold(ctx, value) else ' [Not enough gold]'}"
            )

        print(f"{len(available_items)+1}. Buy nothing")

        choice = input(f"What do you buy? (1-{len(available_items)+1}): ")
        print()

        # Leave shop
        if choice == str(len(available_items) + 1):
            print("You say goodbye to the merchant, and move on.")
            return forward()

        # Purchase item
        elif choice.isnumeric() and 1 <= int(choice) <= len(available_items):

            item, value = available_items[int(choice) - 1]
            item_name = item["name"]
            item_id = item["id"]

            if has_gold(ctx, value):
                article = "an" if item_name[0].lower() in "aeiou" else "a"

                print(f"You buy {article} {item_name}.")
                print(f"[You spent {value} gold]")
                print(f"[You gained {article} {item_name}]")

                give_gold(ctx, value)
                get_item(ctx, item_id)

            else:
                print("You do not have enough gold for that item.")

        else:
            print("Not a valid choice. Try again.")

        press_enter_to_continue()