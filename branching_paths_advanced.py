import time
import advanced_rpg
import random
import pygame
import sys

areas = []
endpoints = []
s = {"name": "Start", "func": lambda _: start()}
normal_areas = [
    {"name": "Goblin Toll", "func": lambda _: goblin_toll()},
    {"name": "Bandits", "func": lambda _: bandits()},
]
random_encounters = [
    {"name": "Traveling Merchant", "func": lambda _: traveling_merchant(), "target": 25},
    {"name": "Traveling Merchant", "func": lambda _: traveling_merchant(), "target": 25},
    {"name": "Traveling Merchant2", "func": lambda _: traveling_merchant2(), "target": 25},
    {"name": "Traveling Merchant2", "func": lambda _: traveling_merchant2(), "target": 25},
    {"name": "Actual Fork", "func": lambda _: actual_fork(), "target": 10},
] 
# (Start + branching areas + 1) must be exactly equal to
# (endpoint_areas + dummy_endpoints + one_way_from_areas)
branching_areas = [
    {"name": "Fork", "func": lambda _: fork()},
    {"name": "Fork2", "func": lambda _: fork()},
]
endpoint_areas = [
    {"name": "Cave", "func": lambda  _, same_entries=False: cave(same_entries)},
    {"name": "Oasis", "func": lambda _: oasis()},
    # {"name": "Dead End", "func": lambda _: dead_end()}
]
dummy_endpoints = [
    {"name": "Dummy Cave", "func": lambda _: cave()},
]
one_way_from_areas = [ # endpoints
    {"name": "Teleporter Trap", "func": lambda first_time: teleporter_trap(first_time)},
]
one_way_to_areas = [ # areas
    {"name": "Teleporter Trap Landing", "func": lambda _: teleporter_trap_landing()},
]
areas_visited = []
connections = {}
side_path = False

def init_environmentals():
    global random_area_encountered, fork_found
    random_area_encountered = False
    fork_found = False

    for _ in areas:
        areas_visited.append(False)

def print_connections(connections):
    with open(advanced_rpg.getCurrentDirectory() + "map.txt", "w") as f:
        for area in list(connections.keys()):
            f.write(f"area {area}: {str(areas[area]["name"])}\n")
            f.write(f"forward: {str(connections[area]['forward'])}\n")
            f.write(f"back: {str(connections[area]['back'])}\n")
            f.write("\n")

def randomize_areas():
    def connect(from_area: int, to_area: int, one_way: bool = False):
        if areas[to_area]["name"] == "Dummy Cave":
            to_area = next(area["index"] for area in areas if area["name"] == "Cave")
        connections[from_area]["forward"].append(to_area)
        if not one_way:
            connections[to_area]["back"].append(from_area)

    def find_area_index(a):
        return next(idx for idx, area in enumerate(areas) if area == a)

    areas.extend(normal_areas)
    areas.extend(random_encounters)
    areas.extend(branching_areas)
    areas.extend(one_way_to_areas)

    endpoints.extend(endpoint_areas)
    endpoints.extend(dummy_endpoints)
    endpoints.extend(one_way_from_areas)

    one_way_pairs = []  # list of (from_area, to_area)
    for one_way_from, one_way_to in zip(one_way_from_areas, one_way_to_areas):
        one_way_pairs.append((one_way_from, one_way_to))

    random.shuffle(endpoints)

    # Step 1: Add first endpoint
    areas.append(endpoints[0])

    random.shuffle(areas)
    areas.insert(0, s)  # Start at beginning

    # Step 2: Set indices
    for i, area in enumerate(areas):
        area["index"] = i

    # Step 3: Insert endpoint for each branching area
    for i, branch in enumerate(branching_areas, start=1):  # start=1, because endpoints[1], endpoints[2], etc.
        branch_index = find_area_index(branch)
        insert_index = random.randint(branch_index + 1, len(areas))
        areas.insert(insert_index, endpoints[i])

    # Step 4: Add the final endpoint (the last one) 
    areas.append(endpoints[-1])

    # Step 5: Re-index after all changes
    for i, area in enumerate(areas):
        area["index"] = i
        connections[i] = {"forward": [], "back": []}

    endpoints.sort(key=lambda ep: ep["index"])
    branching_areas.sort(key=lambda br: br["index"])
    # Step 6: Connect areas
    for i, area in enumerate(areas):
        if area["name"] == "Start":
            connect(i, i + 1)
            connect(i, endpoints[0]["index"] + 1)  # Start connects to first endpoint
        elif area in branching_areas:
            branch_index = branching_areas.index(area)
            connect(i, i + 1)
            connect(i, endpoints[branch_index + 1]["index"] + 1)  # Each branch connects to its matching endpoint
        elif area in one_way_from_areas:
            to_index = 0
            for pair in one_way_pairs:
                if pair[0] == area:
                    to_index = pair[1]["index"]
                    break
            connect(i, to_index, one_way=True)
        elif area in endpoints:
            pass  # Endpoints don't connect forward
        else:
            connect(i, i + 1)

    print_connections(connections)

def main():
    print("\nYou wake up in a dark forest.")
    current = 0
    direction = "forward"
    last_area = 0
    while current is not None and 0 <= current < len(areas):
        if current == 0:
            direction = "forward" 
        current, direction, last_area = area(current, direction, last_area)

def area(num, dir, last_area):
    global random_area_encountered, side_path
    first_time = not areas_visited[num]
    areas_visited[num] = True

    index = None
    direction = None
    area = areas[num]
    
    if area in branching_areas:
        if connections[num]["forward"][0] == connections[num]["forward"][1]:
            return skip(num, dir)
        else:
            if last_area == connections[num]["forward"][1]:
                side_path = True
            else:
                side_path = False

    if area in random_encounters:
        if random.randint(1, 100) > area["target"]:
            return skip(num, dir)
        
    if area in one_way_to_areas:
        if last_area in connections[num]["forward"] or last_area in connections[num]["back"]:
            return skip(num, dir)
        
    same_entries = False
    if len(connections[num]["back"]) > 1 and connections[num]["back"][0] == connections[num]["back"][1]:
        same_entries = True
    
    if same_entries:
        direction, index = area["func"](first_time, same_entries)
    else:
        direction, index = area["func"](first_time)

    if area not in random_encounters:
        press_enter_to_continue()
    elif area in random_encounters and random_area_encountered:
        random_area_encountered = False
        press_enter_to_continue()
    
    
    if side_path:
        d = "back" if direction == "back" else "forward"
    else:
        d = "forward" if direction == dir else "back"

    try:
        if index == -1:
            return last_area, d, num
        elif index == -2:
            index = connections[num][d][0]
            if index == last_area:
                index = connections[num][d][1]
            return index, d, num
        else:
            return connections[num][d][index], d, num
    except:
        print("\nError: failed to route properly.")
        print("num =", num)
        print("last_area =", last_area)
        print("dir =", dir)
        print("direction =", direction)
        print("d =", d)
        print("index =", index)
        print("side_path =", side_path)
        print("random_area_encountered =", random_area_encountered)
        shut_down()
    
def forward(option = 0):
    return "forward", option

def back(option = 0):
    return "back", option

def skip(num, dir):
    direction = "forward"
    index = 0
    d = "forward" if direction == dir else "back"
    return connections[num][d][index], d, num

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
    global random_area_encountered
    random_area_encountered = True
    while True:
        print("\nYou spot a traveling merchant on the side of the path.")
        print("They say they have helpful goods to sell.")
        print("Do you stop to browse their wares?")
        print("1. Yes, stop to browse.")
        print("2. No, keep moving on.")
        choice = input("What action do you take? (1-2): ")
        if choice == "1":
            return shop(("Potion", 5), ("Power Boost", 10), ("Dragon's Bane", 30))   
        elif choice == "2":
            print("You keep going.")
            return forward()
        else:
            print("Not a valid choice. Try again.")

def traveling_merchant2():
    global random_area_encountered
    random_area_encountered = True
    while True:
        print("\nYou spot a traveling merchant on the side of the path.")
        print("They say they have helpful goods to sell.")
        print("Do you stop to browse their wares?")
        print("1. Yes, stop to browse.")
        print("2. No, keep moving on.")
        choice = input("What action do you take? (1-2): ")
        if choice == "1":
            return shop(("Mana Potion", 5), ("Magic Boost", 10), ("Dragon's Bane", 30))   
        elif choice == "2":
            print("You keep going.")
            return forward()
        else:
            print("Not a valid choice. Try again.")

def shop(*items):
    while True:
        print(f"\nYou have {print_gold()} gold.")
        print("The following items are available for purchase: ")

        # Build a list of available items
        available_items = []
        for item in items:
            item_name, value = item
            if item_name == "Dragon's Bane" and has_item("Dragon's Bane"):
                continue  # Skip if player already has Dragon's Bane
            available_items.append(item)

        # Display the available items
        for i, (item_name, value) in enumerate(available_items, 1):
            print(f"{i}. {item_name} ({value} gold){'' if has_gold(value) else ' [Not enough gold]'}")
        print(f"{len(available_items)+1}. Buy nothing")

        choice = input(f"What do you buy? (1-{len(available_items)+1}): ")
        print()

        if choice == str(len(available_items)+1):
            print("You say goodbye to the merchant, and move on.")
            return forward()

        elif choice.isnumeric() and 1 <= int(choice) <= len(available_items):
            item_name, value = available_items[int(choice)-1]
            if has_gold(value):
                print(f"You buy {'a' if item_name[0].lower() not in 'aeiou' else 'an'} {item_name}.")
                print(f"[You spent {value} gold]")
                print(f"[You gained {'a' if item_name[0].lower() not in 'aeiou' else 'an'} {item_name}]")
                give_gold(value)
                get_item(item_name)
            else:
                print("You do not have enough gold for that item.")
        else:
            print("Not a valid choice. Try again.")

        press_enter_to_continue()
   

def cave(same_entries = False):
    while True:
        print("\nYou find a cave entrance.")
        print("The smell of smoke emanates from within.")
        print("Do you enter, turn back, or try the other path?")
        print("1. Enter the cave")
        print("2. Turn back")
        if not same_entries:
            print("3. Other path")
        choice = input("What action do you take? (1-3): ")
        print()
        if choice == "1":
            print("You step into the cave.")
            dragon()
        elif choice == "2":
            print("You go back.")
            return back(-1)
        elif choice == "3" and not same_entries:
            print("You go up the other path.")
            return back(-2)
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
                    print("The dragon says nothing, but prepares to squish you like bug.")
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
    print("You also find a magic broom.")
    if random.randint(1, 100) <= 20:
        print("You are about to fly out of here, but suddenly an Elder Dragon descends into the cave.")
        elder_dragon()
    else:
        print("You hop on the broom and fly off into the sunset. The end.")
    victory()

def elder_dragon():
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
            fight_elder_dragon()
        elif choice == "2":
            print("\nYou pleed with the Elder Dragon to let you go.")
            if check(25, "cha"):
                print("The Elder Dragon takes compasion on you and lets you leave on the broom,\nbut the rest of the treasure must be left behind.")
                give_gold(-1)
                return True
            else:
                print("The Elder Dragon is ammused by your words, but is still goes to kill you.")
                fight_elder_dragon()
                return True
        elif choice == "3":
            fight_elder_dragon()
            return True
        else:
            print("Not a valid choice. Try again.")

def fight_elder_dragon():
    if not fight("Elder Dragon"):
        while alive() and enemy_alive():
            print("\nYou get away momentarily, but the Elder Dragon blocks the only exit and is too big to get around.")
            print("You have to fight it.")
            press_enter_to_continue()
            fight("Elder Dragon", False)
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
            get_gold(10000)
            break
        if choice == "2":
            print("It's probably for the best.")
            break
        else:
            print("Not a valid choice. Try again.")
    return True

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
            # Moving forward toward progression (area 8, not back toward start)
            if side_path:
                side_path = False  # We're no longer in side_path context
                return back(0)  # Move forward in main path
            else:
                return forward(0)  # Normal forward
        elif choice == "2":
            if side_path:
                return back(-1)  # Go back into side path (backtracking into Cave)
            else:
                side_path = True  # Mark that we're going into side path
                return forward(1)  # Move to side path (forward[1])
        elif choice == "3":
            if side_path:
                side_path = False
                return forward(0)  # Back toward start
            else:
                return back(0)  # Normal back
        else:
            print("Not a valid choice. Try again.")

def actual_fork():
    global fork_found, random_area_encountered
    if fork_found:
        return forward()
    fork_found = True
    random_area_encountered = True
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
            attack_up(20)
            break
        elif choice == "2":
            print("You leave the unimportant fork where it is.")
            break
        else:
            print("Not a valid choice. Try again.")
    print("You continue down the path.")
    return forward()

def teleporter_trap(first_time):
    print("\nYou step into a small clearing.")
    print("Looking around, you don't notice anything of interest.")
    if first_time:
        print("Suddenly a purple light shines brightly around you.")
        print("You can't keep your eyes open.")
        return forward()
    else:
        while True:
            print("Suddenly you remember where you are, and don't take another step.\n" \
            "This was the area that teleported you somewhere else in the forrest.\n" \
            "Do you wish to be teleported again?\n" \
            "1. Yes, step in.\n" \
            "2. No, go back.")
            choice = input("Which do you choose? (1-2): ")
            if choice == "1":
                print("\nYou decide to step forward into the light.\nYou are teleported once again.")
                return forward()
            elif choice == "2":
                print("\nYou go back the way you came.")
                return back()
            else:
                print("Not a valid choice. Try again.")

def teleporter_trap_landing():
    while True:
        print("\nYou open your eyes and find yourself not where you were.\n" \
        "The path extends before you and behind.\n" \
        "Where do you go?\n" \
        "1. Forward\n" \
        "2. Back")
        choice = input("Which do you choose? (1-2): ")
        if choice == "1":
            print("\nYou procede down the path ahead of you")
            return forward()
        elif choice == "2":
            print("\nYou turn around and take the path behind you.")
            return back()
        else:
            print("Not a valid choice. Try again.")

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

def has_item(item: str):
    return item in game.player.inventory

def get_item(item: str):
    game.player.inventory.append(item)

def fight(e, new_fight = True):
    print("\n[Open battle window]")
    if new_fight:
        game.battle_prep(e)
    else:
        game.ran_away = False
        game.last_player_action = ""
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
    shut_down()

def victory():
    print("You finished with", game.player.gold, "gold. Well done!")
    shut_down()

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
        game.player.cha += 4
    game.player.dex = 3

def press_enter_to_continue():
    input("\nPress enter to continue...")

def validate_map():
    def check_reachability():
        visited = set()
        stack = [0]  # Start at area 0 (Start)

        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            for neighbor in connections[current]["forward"]:
                stack.append(neighbor)

        print(f"Areas reachable from Start: {sorted(visited)}")
        if len(visited) < len(areas) - len(dummy_endpoints):
            print("Warning: Some areas are unreachable!")
            return False
        else:
            print("All areas are reachable.")
            return True
        
    def check_forward_back_consistency():
        all_good = True
        for i, conn in connections.items():
            for fwd in conn["forward"]:
                if i not in connections[fwd]["back"]:
                    if areas[i] not in one_way_from_areas:
                        print(f"Inconsistent: {areas[i]['name']} -> {areas[fwd]['name']} missing back link!")
                        all_good = False
            for back in conn["back"]:
                if i not in connections[back]["forward"]:
                    print(f"Inconsistent: {areas[i]['name']} <- {areas[back]['name']} missing forward link!")
                    all_good = False
            
        if all_good:
            print("All forward/back connections are consistent.")
        return all_good
    
    def visualize_map():
        def dfs(area, depth=0, visited=None):
            if visited is None:
                visited = set()
            indent = "  " * depth
            area_name = areas[area]["name"]
            forward_links = connections[area]["forward"]

            # Detect dead-end (no forward paths)
            if not forward_links:
                color_code = "\033[91m"  # Red for dead-end
            else:
                color_code = "\033[0m"   # Default

            print(f"{indent}- {color_code}{area_name} (#{area})\033[0m")
            visited.add(area)
            for next_area in forward_links:
                if next_area not in visited:
                    dfs(next_area, depth + 1, visited)
                else:
                    print(f"{'  ' * (depth + 1)}↪ {areas[next_area]['name']} (#{next_area}) [already visited]")
        
        print("\nMAP VISUALIZATION:")
        dfs(0)  # Start from Start (index 0)
        
    while check_reachability() and check_forward_back_consistency():
        global areas, endpoints, connections
        areas = []
        endpoints = []
        connections = {}
        randomize_areas()
    visualize_map()
    shut_down()

def shut_down():
    pygame.quit()
    sys.exit()
    exit()

def test_map():
    randomize_areas()
    validate_map() #infinitely loops looking for an invalid map to properly test if maps are always valid. quits if it finds a problem
    exit()

if __name__ == "__main__":
    # test_map()
    game = advanced_rpg.BattleGame()
    game.run()
    init_player()
    randomize_areas()
    init_environmentals()
    main()
    shut_down()
    