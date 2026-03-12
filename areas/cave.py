# areas/cave.py

import random
import time

from core.area_utils import forward, back, run_away
from core.game_utils import (
    fight,
    get_gold,
    give_gold,
    get_name,
    check,
    victory,
    attack_up,
    rest,
    alive,
    enemy_alive,
)

# --------------------------------------------------
# CAVE ENTRY
# --------------------------------------------------

def cave(ctx, kwargs: dict):
    same_entries = kwargs.get("same_entries", False)
    while True:
        print("\nYou find a cave entrance.")
        print("The smell of smoke emanates from within.")
        print("Do you enter, turn back, or try the other path?")
        print("1. Enter the cave")
        print("2. Turn back")
        num_options = 2

        if not same_entries:
            print("3. Other path")
            num_options += 1

        choice = input(f"What action do you take? (1-{num_options})): ")
        print()

        if choice == "1":
            print("You step into the cave.")
            dragon(ctx)

        elif choice == "2":
            print("You go back.")
            return back(-1)

        elif choice == "3" and not same_entries:
            print("You go up the other path.")
            return back(-2)

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# DRAGON ENCOUNTER
# --------------------------------------------------

def dragon(ctx):
    while True:
        print("\nInside the cave you find a dragon sleeping atop a masive pile treasure.")
        print("1. Wake the dragon.")
        print("2. Try to steal some treasure.")
        print("3. Attack the dragon.")
        print("4. Run away.")

        choice = input("What action do you take? (1-3): ")

        if choice == "1":
            while True:
                print("\nYou boop the dragon on its snout. It stirs and lifts its head.")
                print("\"Why have you come about?\" she asks. \"Do you wish that you were dead?")
                print("1. I want some treasure. Can I have some?")
                print("2. I hate dragons. Prapare to die!")

                options = 2

                if get_name(ctx) == "Bard":
                    options += 1
                    print(f"{options}. Are you a dragon? Because you are firey hot.")

                if False not in ctx.map.visited:
                    options += 1
                    print(f"{options}. I'm stuck in the forest, and can't find a way out. Can you help me?")

                choice = input(f"What action do you take? (1-{options}): ")
                print()

                if choice == "1":
                    print("The dragon looks down at you with a stern expression.")

                    if check(ctx, 15, "cha"):
                        print("But, she reluctantly slides you 30 gold.")
                        get_gold(ctx, 30)
                        print("You thank the dragon and back out of the cave.")
                        return back()
                    else:
                        print("She takes offense at the question and attacks.")
                        if not fight(ctx, "Dragon"):
                            return run_away()
                        dead_dragon(ctx)

                elif choice == "2":
                    print("The dragon says nothing, but prepares to squish you like bug.")
                    if not fight(ctx, "Dragon"):
                        return run_away()
                    dead_dragon(ctx)

                elif choice == "3" and get_name(ctx) == "Bard":
                    print("The dragon considers your words", end="")

                    if check(ctx, 20, "cha"):
                        print(".\nShe is flattered and asks what you need.")
                        print("You tell the dragon you need help getting home.")
                        print("She tells you to climb on her back and she'll fly you out.")
                        print("You fly off into the sunset. The end.")
                        victory(ctx)
                    else:
                        print(" offensive.\nShe wants to bite off you head.")
                        if not fight(ctx, "Dragon"):
                            return run_away()
                        dead_dragon(ctx)

                elif ((choice == "3" and get_name(ctx) != "Bard") or choice == "4") and False not in ctx.map.visited:
                    print("You tell the dragon you need help getting home.")
                    print("She tells you to climb on her back and she'll fly you out.")
                    print("You fly off into the sunset. The end.")
                    victory(ctx)

                else:
                    print("Not a valid choice. Try again.")

        elif choice == "2":
            print("You try to steal some treasure.")
            print("You manage to steal 30 gold.")
            get_gold(ctx, 30)

            if check(ctx, 20, "dex"):
                print("You successfully get away without waking the dragon.")
                return back()
            else:
                print("...but your rumaging wakes the dragon, and she attacks.")
                if not fight(ctx, "Dragon"):
                    return run_away()
                dead_dragon(ctx)

        elif choice == "3":
            print("You charge in to attack the dragon. It hears you and wakes up for the fight.")
            if not fight(ctx, "Dragon"):
                return run_away()
            dead_dragon(ctx)

        elif choice == "4":
            print("You go back.")
            return back()

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# DRAGON DEATH
# --------------------------------------------------

def dead_dragon(ctx):
    print("\nYou slay the dragon.")
    print("You pick up as much gold as you can carry.")
    get_gold(ctx, 1000)

    print("You also find a magic broom.")

    if random.randint(1, 100) <= 20:
        print("You are about to fly out of here, but suddenly an Elder Dragon descends into the cave.")
        elder_dragon(ctx)
    else:
        print("You hop on the broom and fly off into the sunset. The end.")

    victory(ctx)


# --------------------------------------------------
# ELDER DRAGON
# --------------------------------------------------

def elder_dragon(ctx):
    while True:
        print("The Elder Dragon sees his dead child and is not happy about it.")
        print("1. Try to convince the Elder Dragon not to kill you.")
        print("2. Beg for your life.")
        print("3. Attack the Elder Dragon.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            print("\nYou try to come up with some excuse for your situation...")
            time.sleep(2)
            print("...but nothing comes to mind.")
            print("The dragon attacks.")
            fight_elder_dragon(ctx)

        elif choice == "2":
            print("\nYou pleed with the Elder Dragon to let you go.")

            if check(ctx, 25, "cha"):
                print("The Elder Dragon takes compasion on you and lets you leave on the broom,\nbut the rest of the treasure must be left behind.")
                give_gold(ctx, -1)
                return True
            else:
                print("The Elder Dragon is ammused by your words, but is still going to kill you.")
                fight_elder_dragon(ctx)
                return True

        elif choice == "3":
            fight_elder_dragon(ctx)
            return True

        else:
            print("Not a valid choice. Try again.")


# --------------------------------------------------
# ELDER DRAGON FIGHT
# --------------------------------------------------

def fight_elder_dragon(ctx):
    if not fight(ctx, "Elder Dragon"):
        while alive(ctx) and enemy_alive(ctx):
            print("\nYou get away momentarily, but the Elder Dragon blocks the only exit and is too big to get around.")
            print("You have to fight it.")
            input("\nPress enter to continue...")
            fight(ctx, "Elder Dragon", False)

    print("\nFinally the Elder Dragon falls, giving you the freedom you have rightfully earned.")
    print("You are about to leave, when you notice a small bag on the ground next to the Elder Dragon.")
    print("Upon inspection, you recognize this to be a bag of holding, which greatly increases your carrying capacity.")

    while True:
        print("Do you stop to load up on more gold?")
        print("1. Yes, more gold, please.")
        print("2. No, get me out of here before another dragon shows up.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            print("You stop for a moment and fill the bag with gold to capacity.")
            get_gold(ctx, 10000)
            break

        elif choice == "2":
            print("It's probably for the best.")
            break

        else:
            print("Not a valid choice. Try again.")

    return True