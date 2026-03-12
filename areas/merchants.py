# areas/merchants.py

from core.area_utils import forward, press_enter_to_continue
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
                ("Potion", 5),
                ("Power Boost", 10),
                ("Dragon's Bane", 30),
            )

        elif choice == "2":
            print("You keep going.")
            return forward()

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# TRAVELING MERCHANT (MAGIC ITEMS)
# --------------------------------------------------

def traveling_merchant2(ctx, kwargs):
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
                ("Mana Potion", 5),
                ("Magic Boost", 10),
                ("Dragon's Bane", 30),
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

        for item in items:
            item_name, value = item

            # Prevent duplicate Dragon's Bane
            if item_name == "Dragon's Bane" and has_item(ctx, "Dragon's Bane"):
                continue

            available_items.append(item)

        # Display items
        for i, (item_name, value) in enumerate(available_items, 1):
            print(
                f"{i}. {item_name} ({value} gold)"
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

            item_name, value = available_items[int(choice) - 1]

            if has_gold(ctx, value):
                article = "an" if item_name[0].lower() in "aeiou" else "a"

                print(f"You buy {article} {item_name}.")
                print(f"[You spent {value} gold]")
                print(f"[You gained {article} {item_name}]")

                give_gold(ctx, value)
                get_item(item_name)

            else:
                print("You do not have enough gold for that item.")

        else:
            print("Not a valid choice. Try again.")

        press_enter_to_continue()