# areas/fork.py

from core.area_utils import forward, back
from core.game_utils import attack_up

# --------------------------------------------------
# T-INTERSECTION FORK
# --------------------------------------------------

def fork(ctx, kwargs):
    side_path = kwargs["side_path"]

    while True:
        print("\nYou come to a T-intersection", end="")

        if side_path:
            print(".\nYou are coming from the side path.")
        else:
            print(" with a path leading off to the side.")

        print(f"1. {'Turn away from the first area' if side_path else 'Continue straight'}")
        print(f"2. {'Return to the side path' if side_path else 'Take the side path'}")
        print(f"3. {'Turn toward the first area' if side_path else 'Go back the way you came'}")

        choice = input("Which way do you choose? (1-3): ")

        if choice == "1":
            if side_path:
                side_path = False
                return back(0)
            else:
                return forward(0)

        elif choice == "2":
            if side_path:
                return back(-1)
            else:
                side_path = True
                return forward(1)

        elif choice == "3":
            if side_path:
                side_path = False
                return forward(0)
            else:
                return back(0)

        else:
            print("Not a valid choice. Try again.")

# --------------------------------------------------
# JOKE ITEM FORK
# --------------------------------------------------

def actual_fork(ctx, kwargs):
    if ctx.flags.fork_found:
        ctx.map.random_encounter_triggered = False
        return forward()
    
    ctx.flags.fork_found = True

    while True:
        print("\nYou come to a fork in the road.")
        print("Not that kind, this is an actual fork!")
        print("Do you pick it up?")
        print("1. Yes")
        print("2. No")

        choice = input("Which do you choose? (1-2): ")

        if choice == "1":
            print("You pick up the fork and discover it is magical.")
            print("[You equipped \"The Fork\". (+20 Attack)]")
            attack_up(ctx, 20)
            break

        elif choice == "2":
            print("You leave the unimportant fork where it is.")
            break

        else:
            print("Not a valid choice. Try again.")

    print("You continue down the path.")
    return forward()