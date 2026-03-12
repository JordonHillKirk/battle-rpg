# areas/start.py

from core.area_utils import forward

def start(ctx, kwargs):
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