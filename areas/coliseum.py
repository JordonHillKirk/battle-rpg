

import random

from core.area_utils import back, forward, press_enter_to_continue
from core.game_utils import fight, get_gold, give_gold, has_gold, rest


def coliseum_path(ctx, kwargs):
    while True:
        print("You spot a large structure on the side of the road.") 
        print("It looks to be some sort of coliseum.")
        print("Do you wish to investigate?")
        print("1. Yes, stop to investigate.")
        print("2. No, keep walking.")

        choice = input("What action do you take? (1-2): ")

        if choice == "1":
            coliseum(ctx, kwargs)
            while True:
               print("Continue the way you were going before stopping at the coliseum?")
               print("1. Yes, continue on.")
               print("2. No, turn back.")
               choice = input("What action do you take? (1-2): ")
               if choice == "1":
                   print("You continue down the path.")
                   return forward()
               elif choice == "2":
                   print("You decide to go back the way you came.")
                   return back()
               else:
                   print("Not a valid choice. Try again.")

        elif choice == "2":
            print("It's probably for the best.")
            print("You continue on your way.")
            return forward()

        else:
            print("Not a valid choice. Try again.")


def coliseum(ctx, kwargs):
    while True:
        print("\nWelcome to the Orc Coliseum!")
        print("Now accepting contestants for the tournament.")
        print("Entry is 10 gold, but you earn 5 gold for each opponent you defeat.")
        print("Do you wish to enter?")
        if has_gold(ctx, 10):
            print("1. Yes, pay 10 gold.")
        else:
            print("[You do not have enough gold]")
        print("2. No, I'm leaving.")
        choice = input("What action do you take? (1-2): ")
        
        if choice == "1" and has_gold(ctx, 10):
            tournament(ctx, kwargs)
            return
        elif choice == "2":
            print("You decide to leave.")
            return

def tournament(ctx, kwargs):
    give_gold(ctx, 10)
    print("\nGreat! Counting you, there are 16 contestants in the tournament.")
    print("There will be four rounds. In each round you will be paired with a random opponent.")
    print("Try not to die.")
    print("Ready? Begin!")
    press_enter_to_continue()

    contestants = ["Orc Champion",
                   "Orc Elite", "Orc Elite", "Orc Elite", "Orc Elite", "Orc Elite", "Orc Elite",
                   "Orc Shaman", "Orc Shaman", "Orc Shaman",
                   "Orc", "Orc", "Orc", "Orc"
                   "Sneaky Orc"]
    enemies = random.sample(contestants, 4)
    if "Orc Champion" not in enemies:
        enemies[3] = "Orc Champion"
    
    i = 0
    while i < len(enemies):
        if not fight(ctx, enemies[i], allow_forfeit=True):
            break
        print(f"You earned 5 gold for beating the {enemies[i]}.")
        get_gold(ctx, 5)
        i += 1
        press_enter_to_continue()

    if i < len(enemies):
        print("You fought well. You leave with your life at least.")
        return
    else:
        print("You won! You are the new champion.")
        print("The manager comes to you with a special potion to revitalize you.")
        rest(ctx)
        return
    