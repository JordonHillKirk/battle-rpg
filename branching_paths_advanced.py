import advanced_rpg
import random
import pygame
import sys

areas = []
s = {"name": "Start", "func": lambda: start()}
normal_areas = [
    {"name": "Goblin Toll", "func": lambda: goblin_toll()},
    {"name": "Bandits", "func": lambda: bandits()},
]
random_encounters = [
    {"name": "Traveling Merchant", "func": lambda: traveling_merchant(), "target": 25},
    {"name": "Traveling Merchant", "func": lambda: traveling_merchant(), "target": 25},
    {"name": "Actual Fork", "func": lambda: actual_fork(), "target": 10},
]
branching_areas = [
    {"name": "Fork", "func": lambda: fork()},
    # {"name": "Fork2", "func": lambda: fork()},
]
endpoints = [
    {"name": "Cave", "func": lambda: cave()},
    {"name": "Oasis", "func": lambda: oasis()},
    # {"name": "Dead End", "func": lambda: dead_end()}
]
dummy_endpoints = [
    {"name": "Dummy Cave", "func": lambda: cave()},
]
areas_visited = []
connections = {}
side_path = False

def init_environmentals():
    global merchant_found, fork_found, fork_encountered
    merchant_found = False
    fork_found = False
    fork_encountered = False

    for _ in areas:
        areas_visited.append(False)

def print_connections(connections):
    with open(advanced_rpg.getCurrentDirectory() + "map.txt", "w") as f:
        # for area in areas:
        #     f.write(str(area) + "\n")
        # f.write("\n")
        for area in list(connections.keys()):
            f.write(f"area {area}: {str(areas[area]["name"])}\n")
            f.write(f"forward: {str(connections[area]['forward'])}\n")
            f.write(f"back: {str(connections[area]['back'])}\n")
            f.write("\n")

def randomize_areas():
    def connect(from_area: int, to_area: int):
        if areas[to_area]["name"] == "Dummy Cave":
            to_area = next(area["index"] for area in areas if area["name"] == "Cave")
        connections[from_area]["forward"].append(to_area)
        connections[to_area]["back"].append(from_area)

    def find_area_index(a):
        return next(idx for idx, area in enumerate(areas) if area == a)


    areas.extend(normal_areas)
    areas.extend(random_encounters)
    areas.extend(branching_areas)

    endpoints.extend(dummy_endpoints)
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
        elif area in endpoints:
            pass  # Endpoints don't connect forward
        else:
            connect(i, i + 1)

    print_connections(connections)

def main():
    print("You wake up in a dark forest.")
    current = 0
    direction = "forward"
    last_area = 0
    while current is not None and 0 <= current < len(areas):
        if current == 0:
            direction = "forward" 
        current, direction, last_area = area(current, direction, last_area)

def area(num, dir, last_area):
    global merchant_found, side_path, fork_encountered
    areas_visited[num] = True

    i = None
    direction = None
    area = areas[num]
    
    if area["name"] == "Fork" and last_area != connections[num]["forward"][1]:
        side_path = False

    if area in random_encounters:
        if random.randint(1, 100) > area["target"]:
            direction = "forward"
            i = 0
            d = "forward" if direction == dir else "back"
            return connections[num][d][i], d, num
    
    direction, i = area["func"]()
    if area not in random_encounters:
        press_enter_to_continue()
    elif area["name"] == "Traveling Merchant" and merchant_found:
        merchant_found = False
        press_enter_to_continue()
    elif area["name"] == "Actual Fork" and fork_encountered:
        fork_encountered = False
        press_enter_to_continue()
    
    d = "forward" if direction == dir else "back"

    if i == -1:
        return last_area, d, num
    elif i == -2:
        i = connections[num][d][0]
        if i == last_area:
            i = connections[num][d][1]
        return i, d, num
    else:
        return connections[num][d][i], d, num
    
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

def cave():
    while True:
        print("\nYou find a cave entrance.")
        print("The smell of smoke emanates from within.")
        print("Do you enter, turn back, or try the other path?")
        print("1. Enter the cave")
        print("2. Turn back")
        print("3. Other path")
        choice = input("What action do you take? (1-3): ")
        print()
        if choice == "1":
            print("You step into the cave.")
            dragon()
        elif choice == "2":
            print("You go back.")
            return back(-1)
        elif choice == "3":
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
    while True:
        print("\nYou come to a T-intersection", end="")
        if side_path:
            print(".\nYou are coming from the side path.")
        else:
            print(" with a path leading off to the side.")
        print(f"1. {'Turn away from the first area' if side_path else 'Continue straight'}")
        print(f"2. {'Take' if not side_path else 'Return to'} the side path.")
        print(f"3. {'Turn toward the first area' if side_path else 'Go back the way you came'}")
        choice = input("Which way do you choose? (1-3): ")
        if choice == "1":
            if side_path:
                side_path = False
                return back(0)
            return forward(0)
        elif choice == "2":
            if side_path:
                return back(-1)
            side_path = True
            return forward(1)
        elif choice == "3":
            if side_path:
                side_path = False
                return forward()
            return back()
        else:
            print("Not a valid choice. Try again.")

def actual_fork():
    global fork_found, fork_encountered
    if fork_found:
        return forward()
    fork_found = True
    fork_encountered = True
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
        global areas, s, normal_areas, random_encounters, branching_areas, endpoints, dummy_endpoints, connections
        areas = []
        s = {"name": "Start", "func": lambda: start()}
        normal_areas = [
            {"name": "Goblin Toll", "func": lambda: goblin_toll()},
            {"name": "Bandits", "func": lambda: bandits()},
        ]
        random_encounters = [
            {"name": "Traveling Merchant", "func": lambda: traveling_merchant(), "target": 25},
            {"name": "Traveling Merchant", "func": lambda: traveling_merchant(), "target": 25},
            {"name": "Actual Fork", "func": lambda: actual_fork(), "target": 10},
        ]
        branching_areas = [
            {"name": "Fork", "func": lambda: fork()},
            {"name": "Fork2", "func": lambda: fork()},
            {"name": "Fork3", "func": lambda: fork()},
            {"name": "Fork3", "func": lambda: fork()},
            {"name": "Fork3", "func": lambda: fork()},
            {"name": "Fork3", "func": lambda: fork()},
        ]
        endpoints = [
            {"name": "Cave", "func": lambda: cave()},
            {"name": "Oasis", "func": lambda: oasis()},
            {"name": "Dead End", "func": lambda: dead_end()},
            {"name": "Dead End2", "func": lambda: dead_end()},
            {"name": "Dead End2", "func": lambda: dead_end()},
            {"name": "Dead End2", "func": lambda: dead_end()},
            {"name": "Dead End2", "func": lambda: dead_end()},
        ]
        dummy_endpoints = [
            {"name": "Dummy Cave", "func": lambda: cave()},
        ]
        connections = {}
        randomize_areas()
    visualize_map()
    exit()

if __name__ == "__main__":
    game = advanced_rpg.BattleGame()
    game.run()
    init_player()

    randomize_areas()
    # validate_map() #infinitely loops looking for an invalid map to properly test if maps are always valid. quits if it finds a problem

    init_environmentals()
    main()
    pygame.quit()
    sys.exit()
    