
class Entity:
    def __init__(self, name, possessive, hp, attack, defense, moves, inventory):
        self.name = name
        self.possessive = possessive
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.attack_mod = 0
        self.defense = defense
        self.defense_mod = 0
        self.moves = moves
        self.inventory = inventory

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

    def restore_hp(self, val):
        healed = min(self.max_hp, self.hp + val) - self.hp
        self.hp += healed
        return f"Restored {healed} HP."

    def modify_attack(self, val):
        self.attack = self.attack + val
        self.attack_mod += val
        return f"Attack {'decreased' if val < 0 else 'increased'} by {val}."

    def modify_defense(self, val):
        self.defense = self.defense + val
        self.defense_mod += val
        return f"Defense {'decreased' if val < 0 else 'increased'} by {val}."

class Player(Entity):
    def __init__(self, name="Hero", hp=100, max_hp=100, attack=15, defense=5, magic=25, mp=30, max_mp=30, special="", moves=["Slash", "Heavy Strike"], inventory=["Potion","Potion","Power Boost"]):
        super().__init__(name, "Your", hp, attack, defense, moves, inventory)
        self.max_hp = max_hp
        self.magic = magic
        self.magic_mod = 0
        self.mp = mp
        self.max_mp = max_mp
        self.special = special

    def restore_mp(self, val):
        healed = min(self.max_mp, self.mp + val) - self.mp
        self.mp += healed
        return f"Restored {healed} MP."

    def modify_magic(self, val):
        self.magic = self.magic + val
        self.magic_mod += val
        return f"{self.possessive} Magic {'decreased' if val < 0 else 'increased'} by {val}."
    
    def load_player_from_file(lineNum):
        with open(getCurrentDirectory() + "characters.csv", 'r') as f:
            data = {}
            lines = f.readlines()
            header = lines[0]
            line = lines[lineNum]
            keys = header.split(";")
            values = line.split(";")
            for i in range(len(keys)):
                key = keys[i].strip()
                value = values[i].strip()
                if key == "inventory":
                    data[key] = value.split(',') if value.strip() != "" else []
                    for i in range(len(data[key])):
                        data[key][i] = data[key][i].strip()
                elif key in ["hp", "max_hp", "attack", "defense", "magic", "mp", "max_mp"]:
                    data[key] = int(value.strip())
                else:
                    data[key] = value.strip()
            return data
        
class Enemy(Entity):
    def __init__(self, name, hp, attack, defense, moves = ["Bite", "Scratch"], inventory = []):
        super().__init__(name, f"The {name}'s", hp, attack, defense, moves, inventory)
