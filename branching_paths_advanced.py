import advanced_rpg
import random
import pygame
import sys

s = {"name": "Start", "func": lambda: start()}
endpoints = [
    {"name": "Cave", "func": lambda: cave()},
    {"name": "Oasis", "func": lambda: oasis()},
    {"name": "Dead End", "func": lambda: dead_end()}
]
areas = [
    {"name": "Goblin Toll", "func": lambda: goblin_toll()},
    {"name": "Bandits", "func": lambda: bandits()},
    {"name": "Traveling Merchant", "func": lambda: traveling_merchant()}
]
branch = {"name": "Fork", "func": lambda: fork()}
areas_visited = []
connections = {}
side_path = False

def print_connections(connections):
    with open(advanced_rpg.getCurrentDirectory() + "map.txt", "w") as f:
        for area in list(connections.keys()):
            f.write(f"area {area}: {str(areas[area]["name"])}\n")
            f.write(f"forward: {str(connections[area]['forward'])}\n")
            f.write(f"back: {str(connections[area]['back'])}\n")
            f.write("\n")

def randomize_areas():
    def connect(from_area: int, to_area: int):
        connections[from_area]["forward"].append(to_area)
        connections[to_area]["back"].append(from_area)

    branch_index = None
    endpoint0_index = None

    areas.append(branch)
    random.shuffle(endpoints)
    areas.append(endpoints[0])
    random.shuffle(areas)
    areas.insert(0, s)
    for i, area in enumerate(areas):
        if area == branch:
            branch_index = i
        elif area == endpoints[0]:
            endpoint0_index = i
    
    endpoint1_index = random.randint(branch_index + 1, len(areas))
    if endpoint1_index <= endpoint0_index:
        endpoint0_index += 1
    areas.insert(endpoint1_index, endpoints[1])
    areas.append(endpoints[2])
    for i in range(len(areas)):
        connections[i] = {"forward": [], "back": []}
    for i, area in enumerate(areas):
        if area == s:
            connect(i, i+1)
            connect(i, endpoint0_index + 1)
        elif area == branch:
            connect(i, i+1)
            connect(i, endpoint1_index + 1)
        elif area in endpoints:
            pass
        else:
            connect(i, i+1)

    for _ in areas:
        areas_visited.append(False)

    print_connections(connections)

def main():
    print("You wake up in a dark forest.")
    current = 0
    direction = "forward"
    while current is not None and 0 <= current < len(areas):
        current, direction = area(current, direction)

def area(num, dir = "forward"):
    areas_visited[num] = True

    while True:
        global merchant_found
        direction, index = areas[num]["func"]()
        if areas[num]["name"] != "Traveling Merchant" or merchant_found == True:
            press_enter_to_continue()

        if direction == dir:
            return connections[num]["forward"][index], "forward"
        else:
            if index < len(connections[num]["back"]):
                return connections[num]["back"][index], "back"
            else:
                return connections[num]["forward"][index], "forward"

def forward(option = 0):
    return "forward", option
def back(option = 0):
    return "back", option

def start():
    while True:
        print("\nYou see two paths.")
        print("1. Take the left path.")
        print("2. Take the right path.")
        choice = input("Which path do you choose? (1 or 2): ")
        if choice == "1":
            return forward(0)
        elif choice == "2":
            return forward(1)
        else: 
            print("Not a valid choice. Try again.")

def goblin_toll():
    while True:
        print("\nYou run into some goblins. For the moment they do not seem hostile, but they do not let you pass.")
        print("The goblin chief steps up and says, \"Give us 5 gold, and we will let you pass.\"")
        if has_gold(5):
            print("1. Give them 5 gold.")
        else:
            print("[You dont have 5 gold to give]")
        print("2. Attack the goblin chief.")
        print("3. Turn back the way you came.")
        choice = input("What action do you take? (1-3): ")

        if choice == "1" and has_gold(5):
            give_gold(5)
            print("You give them 5 gold. The goblins let you pass.")
            print("You continue down the path.")
            return forward()
        elif choice == "2":
            if not fight("Goblin"):
                return run_away()
            print("\nThe goblins are shocked at what just took place.")
            if random.random() < 0.5:
                print("The shock turns to anger that you killed their chief. You have to run away to not be swarmed by the goblins.")
            else:
                print("The shock turns to joy and celebration. One of the goblins turns to you and says,")
                print("\"Thank you for doing this. We never liked that chief. Here! Take this gold and this Potion, too.\"")
                print("[You got 5 gold.]")
                get_gold(5)
                print("[You got a potion.]")
                get_item("Potion")
            print("You continue down the path.")
            return forward()

        elif choice == "3":
            return back()
        else: 
            print("Not a valid choice. Try again.")

def bandits():
    while True:
        print("\nYou are ambushed by two bandits.")
        print("They demand all your gold and wont let you leave without paying.")
        if has_gold():
            print("1. Give all your gold.")
        else:
            print("[You have no gold to give]")
        print("2. Attack the bandits")
        choice = input("What action do you take? (1-2): ")
        if choice == "1" and has_gold():
            give_gold(-1)
            print("You give up all your gold. The bandits leave.")
            print("You continue down the path.")
            return forward()
        elif choice == "2":
            if not fight("Bandit"):
                return run_away()
            if not fight("Bandit"):
                return run_away()
            print("\nYou loot the bodies, and find a potion and a dagger.")
            print("[You got a potion.]")
            print("[You equipped the dagger. (+2 Attack)]")
            get_item("Potion")
            attack_up(2)
            print("You continue down the path.")
            return forward()
        else: 
            print("Not a valid choice. Try again.")

def traveling_merchant():
    global merchant_found
    merchant_found = False
    if random.randint(1, 100) <= 25:
        merchant_found = True
        while True:
            print("\nYou spot a traveling merchant on the side of the path.")
            print("They say they have helpful goods to sell.")
            print("Do you stop to browse their wares?")
            print("1. Yes, stop to browse.")
            print("2. No, keep moving on.")
            choice = input("What action do you take? (1-2): ")
            if choice == "1":
                while True:
                    print(f"\nYou have {print_gold()} gold.")
                    print("The following items are available for purchase: ")
                    print("1. Potion (5 gold)" + ("" if has_gold(5) else "[Not enough gold]"))
                    print("2. Power Boost (10 gold)" + ("" if has_gold(10) else "[Not enough gold]"))
                    print("3. Dragon's Bane (30 gold)" + ("" if has_gold(30) else "[Not enough gold]"))
                    print("4. Buy nothing")
                    choice = input("What do you buy? (1-4): ") 
                    print()
                    if choice == "1" and has_gold(5):
                        print("You buy a Potion")
                        print("[You spent 5 gold]")
                        print("[You gained a Potion]")
                        give_gold(5)
                        get_item("Potion") 
                    elif choice == "2" and has_gold(10):
                        print("You buy a Power Boost")
                        print("[You spent 10 gold]")
                        print("[You gained a Power Boost]")
                        give_gold(10)
                        get_item("Power Boost")
                    elif choice == "3" and has_gold(30):
                        print("You buy a Dragon's Bane")
                        print("[You spent 30 gold]")
                        print("[You gained a Dragon's Bane]")
                        give_gold(30)
                        get_item("Dragon's Bane")
                    elif choice == "4":
                        print("You say goodbye to the merchant, and move on.")
                        return forward()
                    else:
                        if choice in ["1", "2", "3"]:
                            print("You do not have enough gold for that item.")
                        else:
                            print("Not a valid choice. Try again.")
                    press_enter_to_continue()
                        
            elif choice == "2":
                print("You keep going.")
                return forward()
            else:
                print("Not a valid choice. Try again.")
    else:
        return forward()

def cave():
    while True:
        print("\nYou find a cave entrance.")
        print("The smell of smoke emanates from within.")
        print("Do you enter or turn back?")
        print("1. Enter the cave.")
        print("2. Turn back.")
        choice = input("What action do you take? (1-2): ")
        print()
        if choice == "1":
            print("You step into the cave.")
            dragon()
        elif choice == "2":
            print("You go back.")
            return back()
        else:
            print("Not a valid choice. Try again.")

def dragon():
    while True:
        print("\nInside the cave you find a dragon sleeping atop a masive pile treasure.")
        print("1. Wake the dragon.")
        print("2. Try to steal some treasure.")
        print("3. Attack the dragon.")
        print("4. Run away.")
        choice = input("What action do you take? (1-3): ")
        if choice == "1":
            while True:
                choices = 3
                print("\nYou boop the dragon on its snout. It stirs and lifts its head.")
                print("\"Why have you come about?\" she asks. \"Do you wish that you were dead?")
                print("1. I want some treasure. Can I have some?")
                print("2. I hate dragons. Prapare to die!")
                options = 2
                if get_name() == "Bard":
                    options += 1
                    print(f"{options}. Are you a dragon? Because you are firey hot.")

                if False not in areas_visited:
                    options += 1
                    print(f"{options}. I'm stuck in the forest, and can't find a way out. Can you help me?")
                
                choice = input(f"What action do you take? (1-{options}): ")
                print()
                if choice == "1":
                    print("The dragon looks down at you with a stern expression.")
                    if check(15, "cha"):
                        print("But, she reluctantly slides you 30 gold.")
                        get_gold(30)
                        print("You thank the dragon and back out of the cave.")
                        return back()
                    else:
                        print("She takes offense at the question and attacks.")
                        if not fight("Dragon"):
                            return run_away()
                        dead_dragon()

                elif choice == "2":
                    print("The dragons says nothing, but prepares to squish you like bug.")
                    if not fight("Dragon"):
                        return run_away()
                    dead_dragon()
                
                elif choice == "3" and get_name() == "Bard":
                    print("The dragon considers your words", end="")
                    if check(20, "cha"):
                        print(".\nShe is flattered and asks what you need.")
                        print("You tell the dragon you need help getting home.")
                        print("She tells you to climb on her back and she'll fly you out.")
                        print("You fly off into the sunset. The end.")
                        victory()
                    else:
                        print(" offensive.\nShe wants to bite off you head.")
                        if not fight("Dragon"):
                            return run_away()
                        dead_dragon()

                elif ((choice == "3" and get_name != "Bard") or choice == "4") and False not in areas_visited:
                    print("You tell the dragon you need help getting home.")
                    print("She tells you to climb on her back and she'll fly you out.")
                    print("You fly off into the sunset. The end.")
                    victory()
                
                else:
                    print("Not a valid choice. Try again.")

        elif choice == "2":
            print("You try to steal some treasure.")
            print("You manage to steal 30 gold.")
            get_gold(30)
            if check(20, "dex"):
                print("You successfully get away without waking the dragon.")
                return back()
            else:
                print("...but your rumaging wakes the dragon, and she attacks.")
                if not fight("Dragon"):
                    return run_away()
                dead_dragon()

        if choice == "3":
            print("You charge in to attack the dragon. It hears you and wakes up for the fight.")
            if not fight("Dragon"):
                return run_away()
            dead_dragon()

        elif choice == "4":
            print("You go back.")
            return back()
        else:
            print("Not a valid choice. Try again.")

def dead_dragon():
    print("\nYou slay the dragon.")
    print("You pick up as much gold as you can carry.")
    get_gold(1000)
    print("You also find a magic broom.\nYou hop on and fly off into the sunset. The end.")
    victory()

def oasis():
    while True:
        print("\nYou find a small stream with only dense forest on the other side. There is nowhere to go but back.")
        print("1. Rest for a bit before going back.")
        print("2. Go back.")
        choice = input("What action do you take? (1-2): ")
        if choice == "1":
            print("You sit down to rest for a bit. The cool water is very refreshing.")
            rest()
            print("After you finish resting, you get up and go back up the path.")
            return back()
        elif choice == "2":
            print("You turn back the way you came.")
            return back()
        else: 
            print("Not a valid choice. Try again.")

def dead_end():
    print("\nYou reach a dead end and must turn back.")
    return back()

def fork():
    global side_path
    print("\nYou come to a fork in the road.")
    print("1. Continue Straight")
    print(f"2. {'Take' if not side_path else 'Return to'} the side path.")
    print("3. Go Back")
    choice = input("> ")
    if choice == "1":
        side_path = False
        return forward(0)
    if choice == "2":
        side_path = True
        return forward(1)
    if choice == "3":
        side_path = False
        return back()

def get_name():
    return game.player.name

def has_gold(val = 0):
    return game.player.gold >= val and game.player.gold > 0

def give_gold(val: int):
    if val == -1:
        game.player.gold = 0
    else:
        game.player.gold = max(game.player.gold - val, 0)

def get_gold(val: int):
    game.player.gold += val

def print_gold():
    return game.player.gold

def get_item(item: str):
    game.player.inventory.append(item)

def fight(e):
    game.battle_prep(e)
    while alive() and enemy_alive() and not game.ran_away:
        game.make_buttons()
        game.run()
        if game.ran_away:
            return False
    if not alive():
        death()
    return True

def alive():
    return game.player.hp > 0

def enemy_alive():
    return game.enemy.hp > 0

def run_away():
    print("You somehow manage to escape back the way you came.")
    return back()

def attack_up(val: int):
    game.player.attack += val
    
def defense_up(val: int):
    game.player.defense += val

def death():
    print("\nYou have died. Your journey is over.")
    input()
    exit()

def victory():
    print("You finished with", game.player.gold, "gold. Well done!")
    exit()

def check(dc, stat):
    return random.randint(1, 20) + getattr(game.player, stat) > dc

def rest():
    heal_hp()
    heal_mp()
    print("Your HP and MP have been restored to full.")

def heal_hp(val:int = None):
    if val:
        game.player.hp = min(game.player.max_hp, game.player.hp + val)
    else:
        game.player.hp = game.player.max_hp

def heal_mp(val:int = None):
    if val:
        game.player.mp = min(game.player.max_mp, game.player.mp + val)
    else:
        game.player.mp = game.player.max_mp

def init_player():
    game.player.gold = 5
    game.player.cha = 1
    if game.player.name == "Bard":
        game.player.cha += 3
    game.player.dex = 3

def press_enter_to_continue():
    input("\nPress enter to continue...")

if __name__ == "__main__":
    game = advanced_rpg.BattleGame()
    game.run()
    init_player()
    randomize_areas()
    main()
    pygame.quit()
    sys.exit()
    