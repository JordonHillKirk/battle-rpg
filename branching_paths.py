import simple_rpg

gold = 5

def main():
    print("You wake up in a dark forest.")
    start()

def start():
    while True:
        print("\nYou see two paths.")
        print("1. Take the left path.")
        print("2. Take the right path.")
        choice = input("Which path do you choose? (1 or 2): ")

        if choice == "1":
            left_path()
            break
        elif choice == "2":
            right_path()
            break
        else: 
            print("Not a valid choice. Try again.")

def left_path():
    print("\nYou run into some goblins. For the moment they do not seem hostile, but they do not let you pass.")
    print("The goblin chief steps up and says, 'Give us your gold.'")
    print("1. Give them all your gold.")
    print("2. Attack the goblin chief.")
    print("3. Turn back the way you came.")
    choice = input("What action do you take? (1-3): ")

    if choice == "1":
        global gold
        gold = 0
        print("You give up all your gold. The goblins let you pass.")
    elif choice == "2":
        simple_rpg.main("Goblin")
        pass
    elif choice == "3":
        start()
    else: 
        print("Not a valid choice. Try again.")

def right_path():
    pass


if __name__ == "__main__":
    simple_rpg.load_player()
    main()