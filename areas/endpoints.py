# areas/endpoints.py

from core.area_utils import back
from core.game_utils import rest


# --------------------------------------------------
# OASIS
# --------------------------------------------------

def oasis(ctx, kwargs):
    while True:
        print("\nYou find a small stream with only dense forest on the other side. There is nowhere to go but back.")
        print("1. Rest for a bit before going back.")
        print("2. Go back.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            print("You sit down to rest for a bit. The cool water is very refreshing.")
            rest(ctx)
            print("After you finish resting, you get up and go back up the path.")
            return back()

        elif choice == "2":
            print("You turn back the way you came.")
            return back()

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# DEAD END
# --------------------------------------------------

def dead_end(ctx, kwargs):
    print("\nYou reach a dead end and must turn back.")
    return back()