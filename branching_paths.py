import simple_rpg
import random

areas = [
    lambda: goblin_toll(),
    lambda: bandits()
]

def main():
    print("You wake up in a dark forest.")
    start()

def randomize_areas():
    random.shuffle(areas)

def start():
    while True:
        print("\nYou see two paths.")
        print("1. Take the left path.")
        print("2. Take the right path.")
        choice = input("Which path do you choose? (1 or 2): ")

        if choice == "1":
            area1()
            break
        elif choice == "2":
            area2()
            break
        else: 
            print("Not a valid choice. Try again.")

def area1():
    areas[0]()
    cave()

def area2():
    areas[1]()
    cave()


def goblin_toll():
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

    elif choice == "3":
        start()
    else: 
        print("Not a valid choice. Try again.")

def bandits():
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
    elif choice == "2":
        fight("Bandit")
        fight("Bandit")
        print("\nYou loot the bodies, and find a potion and a dagger.")
        print("[You got a potion.]")
        print("[You equipped the dagger. (+2 Attack)]")
        get_item("Potion")
        attack_up(2)
    else: 
        print("Not a valid choice. Try again.")

def cave():
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
    else:
        print("Not a valid choice. Try again.")

def dragon():
    print("\nInside the cave you find a dragon sleeping atop a masive pile treasure.")
    print("1. Wake the dragon.")
    print("2. Try to steal some treasure.")
    print("3. Attack the dragon.")
    print("4. Run away.")
    choice = input("What action do you take? (1-3): ")
    if choice == "1":
        print("You boop the dragon on its snout. It stirs and lifts its head.")
        print("\"Why have you come about?\" she asks. \"Do you wish that you were dead?")
        print("1. I want some treasure. Can I have some?")
        print("2. I hate dragons. Prapare to die!")

        # TODO: Only allow Bards this option
        print("3. Are you a dragon? Because you are firey hot.")

        # TODO: Option appears only once all areas have been visited.
        print("4. I'm stuck in the forest, and can't find a way out. Can you help me?")
        
        choice = input("What action do you take? (1-4): ")
        if choice == "1":
            print("The dragon looks down at you with a stern expression.")
            if check(15, "Cha"):
                print("But, she reluctantly slides you 30 gold.")
                get_gold(30)
                print("You thank the dragon and back out of the cave.")
                cave()
            else:
                print("She takes offense at the question and attacks.")
                fight("Dragon")
                dead_dragon()

        elif choice == "2":
            print("The dragons says nothing, but prepares to squish you like bug.")
            fight("Dragon")
            dead_dragon()
        
        elif choice == "3":
            print("The dragon considers your words", end="")
            if check(20, "Cha"):
                print(".\nShe is flattered and asks what you need.")
                print("You tell the dragon you need help getting home.")
                print("She tells you to climbe on her back and she'll fly you out.")
                print("You fly off into the sunset. The end.")
            else:
                print(" offensive.\nShe wants to bite off you head.")
                fight("Dragon")
                dead_dragon()

        elif choice == "4":
            print("You tell the dragon you need help getting home.")
            print("She tells you to climb on her back and she'll fly you out.")
            print("You fly off into the sunset. The end.")
        
        else:
            print("Not a valid choice. Try again.")

    elif choice == "2":
        print("You try to steal some treasure.")
        print("You manage to steal 30 gold.")
        get_gold(30)
        if check(20, "Dex"):
            print("You successfully get away without waking the dragon.")
            cave()
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
        cave()
    else:
        print("Not a valid choice. Try again.")

def dead_dragon():
    print("You slay the dragon.")
    print("You pick up as much gold as you can carry.")
    get_gold(1000)
    print("You also find a magic broom.\nYou hop on and fly off into the sunset. The end.")

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

def check(dc, stat):
    return random.randint(1, 20) + simple_rpg.player[stat] > dc

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