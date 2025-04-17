import os
import random

def getCurrentDirectory():
    return os.path.dirname(os.path.realpath(__file__)) + "\\"
    
path = getCurrentDirectory()
file = "characters.csv"

player = {}
moves = {
    "Slash": lambda atk: atk + 5,
    "Heavy Slash": lambda atk: atk * 2 - 3
}
player["inventory"] = ["Potion", "Potion", "Power Boost"]

enemies = [
    {"name": "Goblin", "hp": 50, "max_hp": 50, "attack": 10, "defense": 2},
    {"name": "Orc", "hp": 80, "max_hp": 80, "attack": 12, "defense": 4},
    {"name": "Dragon", "hp": 150, "max_hp": 150, "attack": 20, "defense": 8},
    {"name": "Bandit", "hp": 75, "max_hp": 75, "attack": 10, "defense": 5}
]

items = {
    "Potion": lambda stats: {"hp": min(stats["max_hp"], stats["hp"] + 20)},
    "Power Boost": lambda stats: {"attack": stats["attack"] + 5}
}

spells = {
    "Fireball": {
        "cost": 10,
        "desc": "Deal magic - enemy defense + 5 damage",
        "action": lambda caster, target: max(0, (caster["magic"] - target["defense"])) + 5
    },
    "Heal": {
        "cost": 8,
        "desc": "Restore up to 20 HP",
        "action": lambda caster, _: min(caster["max_hp"] - caster["hp"], 20)
    },
    "Lambda": {
        "cost": 5,
        "desc": "Create a sheep to block an attack.",
        "action": lambda _, _2: random.choice([1, 2])
    },
}

def get_character(characters):
    print("Select a character:")
    for i, name in enumerate(characters, 1):
        print(f"{i}. {name}")
    choice = input("> ")
    return int(choice)

def load_player():
    with open(path + file, "r") as f:
        lines = f.readlines()
        characters = []
        for line in lines:
            if line != lines[0]:
                characters.append(line.split(";")[0])
        character = get_character(characters)
        line = lines[character]
        split = line.split(";")
        player["name"] = split[0].strip()
        player["hp"] = int(split[1].strip())
        player["max_hp"] = int(split[2].strip())
        player["attack"] = int(split[3].strip())
        player["defense"] = int(split[4].strip())
        player["magic"] = int(split[5].strip())
        player["mp"] = int(split[6].strip())
        player["max_mp"] = int(split[7].strip())

def damage_variance(damage):
    return random.randint(damage - 3, damage + 3)

def show_health_bar(name, hp, max_hp, mp = None, max_mp = None):
    bar_length = 20
    filled_length = int(bar_length * hp / max_hp)
    bar_color = "\U0001F7E9"
    if hp <= max_hp / 2:
        bar_color = "\U0001F7E8"
    if hp <= max_hp / 4:
        bar_color = "\U0001F7E5"
    bar = bar_color * filled_length + "\U00002B1b" * (bar_length - filled_length)
    print(f"{name}:\t[{bar}] {hp}/{max_hp} HP")
    if mp:
        filled_length = int(bar_length * mp / max_mp)
        bar_color = "\U0001F7E6"
        bar = bar_color * filled_length + "\U00002B1b" * (bar_length - filled_length)
        print(f"\t[{bar}] {mp}/{max_mp} MP")

def main(e: str = None):
    lambda_count = 0
    lambda_turn_count = 0
    used_lambda = False
    enemy = None
    if e:
        for en in enemies:
            if en["name"] == e:
                enemy = en
                break
        if enemy == None:
            enemy = random.choice(enemies)
    else:
        enemy = random.choice(enemies)
    enemy_moves = {"Bite": enemy["attack"] + 2, "Scratch": enemy["attack"] - 2}
    if enemy["name"] == "Dragon":
        enemy_moves["Fire Breath"] = 25
    print(f"A wild {enemy['name']} appears.")

    while player["hp"] > 0 and enemy["hp"] > 0:
        player["mp"] = min(player["mp"] + 1, player["max_mp"])
        show_health_bar(player["name"], player["hp"], player["max_hp"], player["mp"], player["max_mp"])
        show_health_bar(enemy["name"], enemy["hp"], enemy["max_hp"])

        #player attack
        print("\nChoose and action:")
        print("1. Attack")
        print("2. Use Item")
        print("3. Cast Magic")
        print("4. Run away")
        action = input("> ").strip()

        if action == "1":
            print("\nAvailable Moves:")
            for i, (move, data) in enumerate(moves.items(), 1):
                print(f"{i}. {move}")
            choice = input("> ").strip()
            move_names = list(moves.keys())

            if choice.isdigit() and 1 <= int(choice) <= len(moves):
                move = move_names[int(choice) - 1]
                data = moves[move]
                damage = max(1, damage_variance(data(player["attack"] - enemy["defense"])))
                enemy["hp"] -= damage
                print(f"You used {move}! {enemy['name']} takes {damage} damage.")
            else:
                print("Invalid move! Try again.")
                continue

        elif action == "2":
            print("\nChoose an item: ")
            for i, item in enumerate(player["inventory"], 1):
                print(f"{i}. {item}")
            choice = input("> ").strip()

            if choice.isdigit() and 1 <= int(choice) <= len(player["inventory"]):
                item = player["inventory"][int(choice) - 1]
                effect = items[item](player)
                player.update(effect)
                player["inventory"].remove(item)
                print(f"You used {item}! New Stats: {effect}")
            else:
                print("You don't have that item. You wasted your turn looking for it.")

        elif action == "3":
            print("\nChoose a spell:")
            for i, (spell, data) in enumerate(spells.items(), 1):
                print(f"{i}. {spell} (Cost: {data["cost"]} MP) - {data["desc"]}")
            spell_choice = input("> ")
            spell_names = list(spells.keys())

            if spell_choice.isdigit() and 1 <= int(spell_choice) <= len(spells):
                spell = spell_names[int(spell_choice) - 1]
                data = spells[spell]
                if player["mp"] >= data["cost"]:
                    player["mp"] -= data["cost"]
                    result = data["action"](player, enemy)
                    if spell == "Heal":
                        player["hp"] += result
                        print(f"You cast {spell} and healed {result} HP!")
                    elif spell == "Lambda":
                        used_lambda = True
                        lambda_turn_count = result
                        print(f"You cast {spell} and summoned a sheep!")
                    else:
                        enemy["hp"] -= result
                        print(f"You cast {spell} and dealt {result} damage!")
                else:
                    print("Not enough MP!")
            else:
                print("Invalid spell.") 
    
        elif action == "4":
            if player["hp"] >= enemy["hp"] or random.random() <= 1 - (enemy["hp"] / enemy["max_hp"]):
                print("You escapped successfully!")
                break
            else:
                print("You failed to run away!")
        
        else:
            print("Invalid action")
            continue

        if enemy["hp"] <= 0:
            print(f"{enemy['name']} has been defeated!")
            break

        #enemy attack
        if enemy["name"] == "Bandit" and enemy["hp"] <= 20:
            print(f"{enemy['name']} used a potion and resorted 20 health.")
            enemy["hp"] += 20
        else:
            enemy_move = random.choice(list(enemy_moves.keys()))
            if enemy["hp"] < enemy["max_hp"] / 2 and enemy_move != "Bite":
                enemy_move = random.choice(list(enemy_moves.keys()))
            damage = max(1, damage_variance(enemy_moves[enemy_move] - player["defense"]))
            print(f"The {enemy['name']} used {enemy_move}!", end=" ")
            if not used_lambda:
                print(f"You take {damage} damage.")
                player["hp"] -= damage
            else:
                print("But it was blocked by the sheep.")
                lambda_turn_count -= 1
                if lambda_turn_count == 0:
                    used_lambda = False
                    print("The sheep was killed. Poor sheep.")
                if enemy["name"] == "Dragon" and enemy_move == "Bite":
                    lambda_count += 1
                    if lambda_count == 20:
                        print("The Dragon got full and flew away!")
                        break

        if player["hp"] <= 0:
            print("You have been defeated.")
    
    print("The battle is over.")

def init(e = None):
    load_player()
    main(e)

if __name__ == "__main__":
    load_player()
    main()