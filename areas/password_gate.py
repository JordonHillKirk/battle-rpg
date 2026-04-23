import random

from core.area_utils import back, forward

def create_password_gate_areas(ctx):
    areas = []

    possible_passwords = ["lost", "stone", "sword", "dragon", "cave"]
    password = random.choice(possible_passwords)

    ctx.flags.password_gate_password = password
    ctx.flags.password_gate_found_letters = {}
    ctx.flags.password_gate_active = False

    # letter trees
    for i, letter in enumerate(password):
        areas.append({
            "name": f"Letter Tree {letter.upper()}",
            "func": tree,
            "type": "password_letter",
            "kwargs": {"index": i},
            "target": 10,
            "rules": ["random_encounter"],
            "is_password_tree": True,
        })

    return areas

def get_letter(ctx, i):
    return ctx.flags.password_gate_password[i].upper()

def display_letters(ctx):
    letters = ctx.flags.password_gate_found_letters

    if not letters:
        return ""

    sorted_keys = sorted(letters.keys())

    result = " ("
    for key in sorted_keys:
        result += letters[key]
    result += ")"

    return result

def tree(ctx, kwargs):
    i = kwargs["index"]

    if i in ctx.flags.password_gate_found_letters:
        print("This tree has already been searched.")
        return forward()

    letter = get_letter(ctx, i)
    print(f"You see a letter carved into a tree: {letter}")

    ctx.flags.password_gate_found_letters[i] = letter

    # disable this specific tree
    current_area_index = ctx.map.current_area
    ctx.map.areas[current_area_index]["target"] = 0

    print("You make note of it and continue on.")
    return forward()

def password_gate(ctx, kwargs):
    if not ctx.flags.password_gate_active:
        ctx.flags.password_gate_active = True

        for node in ctx.map.areas:
            if "is_password_tree" in node.keys()  and node["target"] != 0:
                node["target"] = 100

    print("You come accross a large stone gate with an enscription:")
    print("\"Enter you may, if the password you say.\"")
    print("\"Find the clues among the trees. Now you should be able to find them with ease.\"")
    while True:
        guess = input(f"What is the password{display_letters(ctx)}: ")
        if guess.lower() == ctx.flags.password_gate_password.lower():
            print("The door shifts and opens. You pass through and continue on.")
            return forward()
        else:
            print("Nothing happens. That must not be the password.")
            print("Try again?")
            print("1. Yes")
            print("2. No, Turn back and look for the clues")
            choice = input("What action do you take? (1-2): ")
        
            if choice == "1":
                continue
            elif choice == "2":
                print("You decide to turn back.")
                return back()
