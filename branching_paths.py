import simple_rpg
import random

areas = [
    lambda: goblin_toll(),
    lambda: bandits()
]
endpoints = [
    lambda: cave(),
    lambda: oasis()
]
areas_visitied = []

def main():
    print("You wake up in a dark forest.")
    start()

def randomize_areas():
    global cave_num
    random.shuffle(endpoints)
    areas.append(endpoints[0])
    random.shuffle(areas)
    areas.append(endpoints[1])
    cave_num = areas.index(endpoints[0])
    for _ in areas:
        areas_visitied.append(False)

def start():
    while True:
        print("\nYou see two paths.")
        print("1. Take the left path.")
        print("2. Take the right path.")
        choice = input("Which path do you choose? (1 or 2): ")

        if choice == "1":
            area(0)
            
        elif choice == "2":
            area(cave_num + 1)
            
        else: 
            print("Not a valid choice. Try again.")

def area(i):
    back = False
    areas_visitied[i] = True
    while True:
        forward = areas[i]()
        press_enter_to_continue()
        if forward != back:
            back = not area(i + 1)
        else:
            return False

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
            print("You give up all your gold. The goblins let you pass.")
            print("You continue down the path.")
            return True
        elif choice == "2":
            fight("Goblin")
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
            return True

        elif choice == "3":
            return False
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
            return True
        elif choice == "2":
            fight("Bandit")
            fight("Bandit")
            print("\nYou loot the bodies, and find a potion and a dagger.")
            print("[You got a potion.]")
            print("[You equipped the dagger. (+2 Attack)]")
            get_item("Potion")
            attack_up(2)
            return True
        else: 
            print("Not a valid choice. Try again.")

def cave():
    while True:
        print("\nYou find a cave entrance.")
        print("The smell of smoke emanates from within.")
        print("Do you enter or turn back?")
        print("1. Enter the cave.")
        print("2. Turn back.")
        choice = input("What action do you take? (1-2): ")
        if choice == "1":
            print("You step into the cave.")
            dragon()
        elif choice == "2":
            print("You go back.")
            return False
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
                print("You boop the dragon on its snout. It stirs and lifts its head.")
                print("\"Why have you come about?\" she asks. \"Do you wish that you were dead?")
                print("1. I want some treasure. Can I have some?")
                print("2. I hate dragons. Prapare to die!")
                options = 2
                if get_name() == "Bard":
                    options += 1
                    print(f"{options}. Are you a dragon? Because you are firey hot.")

                if False not in areas_visitied:
                    options += 1
                    print(f"{options}. I'm stuck in the forest, and can't find a way out. Can you help me?")
                
                choice = input(f"What action do you take? (1-{options}): ")
                if choice == "1":
                    print("The dragon looks down at you with a stern expression.")
                    if check(15, "Cha"):
                        print("But, she reluctantly slides you 30 gold.")
                        get_gold(30)
                        print("You thank the dragon and back out of the cave.")
                        return False
                    else:
                        print("She takes offense at the question and attacks.")
                        fight("Dragon")
                        dead_dragon()

                elif choice == "2":
                    print("The dragons says nothing, but prepares to squish you like bug.")
                    fight("Dragon")
                    dead_dragon()
                
                elif choice == "3" and get_name() == "Bard":
                    print("The dragon considers your words", end="")
                    if check(20, "Cha"):
                        print(".\nShe is flattered and asks what you need.")
                        print("You tell the dragon you need help getting home.")
                        print("She tells you to climb on her back and she'll fly you out.")
                        print("You fly off into the sunset. The end.")
                        victory()
                    else:
                        print(" offensive.\nShe wants to bite off you head.")
                        fight("Dragon")
                        dead_dragon()

                elif ((choice == "3" and get_name != "Bard") or choice == "4") and False not in areas_visitied:
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
            if check(20, "Dex"):
                print("You successfully get away without waking the dragon.")
                return False
            else:
                print("...but your rumaging wakes the dragon, and she attacks.")
                fight("Dragon")
                dead_dragon()

        if choice == "3":
            print("You charge in to attack the dragon. It hears you and wakes up for the fight.")
            fight("Dragon")
            dead_dragon()

        elif choice == "4":
            print("You go back.")
            return False
        else:
            print("Not a valid choice. Try again.")

def dead_dragon():
    print("You slay the dragon.")
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
            return False
        elif choice == "2":
            print("You turn back the way you came.")
            return False
        else: 
            print("Not a valid choice. Try again.")

def get_name():
    return simple_rpg.player["name"] 

def has_gold(val = 0):
    return simple_rpg.player["gold"] >= val

def give_gold(val: int):
    if val == -1:
        simple_rpg.player["gold"] = 0
    else:
        simple_rpg.player["gold"] = max(simple_rpg.player["gold"] - val, 0)

def get_gold(val: int):
    simple_rpg.player["gold"] += val

def get_item(item: str):
    simple_rpg.player["inventory"].append("Potion")

def fight(e):
    simple_rpg.main(e)
    if not alive():
        death()

def alive():
    return simple_rpg.player["hp"] > 0

def attack_up(val: int):
    simple_rpg.player["attack"] += val
    
def defense_up(val: int):
    simple_rpg.player["defense"] += val

def death():
    print("\nYou have died. Your journey is over.")
    input()
    exit()

def victory():
    print("You finished with", simple_rpg.player["gold"], "gold. Well done!")
    exit()

def check(dc, stat):
    return random.randint(1, 20) + simple_rpg.player[stat] > dc

def rest():
    heal_hp()
    heal_mp()
    print("Your HP and MP have been restored to full.")

def heal_hp(val:int = None):
    if val:
        simple_rpg.player["hp"] = min(simple_rpg.player["max_hp"], simple_rpg.player["hp"] + val)
    else:
        simple_rpg.player["hp"] = simple_rpg.player["max_hp"]

def heal_mp(val:int = None):
    if val:
        simple_rpg.player["mp"] = min(simple_rpg.player["max_mp"], simple_rpg.player["mp"] + val)
    else:
        simple_rpg.player["mp"] = simple_rpg.player["max_mp"]

def press_enter_to_continue():
    input("\nPress enter to continue...")

if __name__ == "__main__":
    simple_rpg.load_player()
    simple_rpg.player["gold"] = 5
    simple_rpg.player["Cha"] = 1
    if simple_rpg.player["name"] == "Bard":
        simple_rpg.player["Cha"] += 3
    simple_rpg.player["Dex"] = 3
    randomize_areas()
    main()
    print("You finished with", simple_rpg.player["gold"], "gold. Well done!")