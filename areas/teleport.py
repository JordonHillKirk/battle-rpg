# areas/teleport.py

from core.area_utils import forward, back


# --------------------------------------------------
# TELEPORTER TRAP (ONE-WAY SOURCE)
# --------------------------------------------------

def teleporter_trap(ctx, kwargs):
    first_time = kwargs.get("first_time", True)

    print("\nYou step into a small clearing.")
    print("Looking around, you don't notice anything of interest.")

    if first_time:
        print("Suddenly a purple light shines brightly around you.")
        print("You can't keep your eyes open.")
        ctx.arrival.teleport = True
        return forward()

    else:
        while True:
            print(
                "Suddenly you remember where you are, and don't take another step.\n"
                "This was the area that teleported you somewhere else in the forest.\n"
                "Do you wish to be teleported again?\n"
                "1. Yes, step in.\n"
                "2. No, go back."
            )

            choice = input("Which do you choose? (1-2): ")

            if choice == "1":
                print("\nYou decide to step forward into the light.\nYou are teleported once again.")
                ctx.arrival.teleport = True
                return forward()

            elif choice == "2":
                print("\nYou go back the way you came.")
                return back()

            else:
                print("Not a valid choice. Try again.")


# --------------------------------------------------
# TELEPORT LANDING (DESTINATION AREA)
# --------------------------------------------------

def teleporter_trap_landing(ctx, kwargs):
    while True:
        print(
            "\nYou open your eyes and find yourself not where you were.\n"
            "The path extends before you and behind.\n"
            "Where do you go?\n"
            "1. Forward\n"
            "2. Back"
        )

        choice = input("Which do you choose? (1-2): ")

        if choice == "1":
            print("\nYou procede down the path ahead of you")
            return forward()

        elif choice == "2":
            print("\nYou turn around and take the path behind you.")
            return back()

        else:
            print("Not a valid choice. Try again.")