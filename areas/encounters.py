# areas/encounters.py

import random
from core.area_utils import forward, back, run_away
from core.game_utils import *

def goblin_toll(ctx, kwargs):
    while True:
        print("\nYou run into some goblins. For the moment they do not seem hostile, but they do not let you pass.")
        print("The goblin chief steps up and says, \"Give us 5 gold, and we will let you pass.\"")
        if has_gold(ctx, 5):
            print("1. Give them 5 gold.")
        else:
            print("[You dont have 5 gold to give]")
        print("2. Attack the goblin chief.")
        print("3. Turn back the way you came.")
        choice = input("What action do you take? (1-3): ")

        if choice == "1" and has_gold(ctx, 5):
            give_gold(ctx, 5)
            print("You give them 5 gold. The goblins let you pass.")
            print("You continue down the path.")
            return forward()
        elif choice == "2":
            if not fight(ctx, "Goblin"):
                return run_away()
            print("\nThe goblins are shocked at what just took place.")
            if random.random() < 0.5:
                print("The shock turns to anger that you killed their chief. You have to run away to not be swarmed by the goblins.")
            else:
                print("The shock turns to joy and celebration. One of the goblins turns to you and says,")
                print("\"Thank you for doing this. We never liked that chief. Here! Take this gold and this Potion, too.\"")
                print("[You got 5 gold.]")
                get_gold(ctx, 5)
                print("[You got a potion.]")
                get_item(ctx, "potion")
            print("You continue down the path.")
            return forward()

        elif choice == "3":
            return back()
        else: 
            print("Not a valid choice. Try again.")
        
def bandits(ctx, kwargs):
    while True:
        print("\nYou are ambushed by two bandits.")
        print("They demand all your gold and wont let you leave without paying.")
        if has_gold(ctx):
            print("1. Give all your gold.")
        else:
            print("[You have no gold to give]")
        print("2. Attack the bandits")
        choice = input("What action do you take? (1-2): ")
        if choice == "1" and has_gold(ctx):
            give_gold(ctx, -1)
            print("You give up all your gold. The bandits leave.")
            print("You continue down the path.")
            return forward()
        elif choice == "2":
            potion = False
            if not fight(ctx, "Bandit"):
                return run_away()
            if "potion" in ctx.game.enemy.inventory:
                potion = True
            if not fight(ctx, "Bandit"):
                return run_away()
            if "potion" in ctx.game.enemy.inventory:
                potion = True
            print("\nYou loot the bodies, and find a dagger.")
            if potion:
                print("You also find an unused potion.")
            print("[You equipped the dagger. (+2 Attack)]")
            if potion:
                print("[You got a Potion.]")
                get_item(ctx, "potion")
            attack_up(ctx, 2)
            print("You continue down the path.")
            return forward()
        else: 
            print("Not a valid choice. Try again.")