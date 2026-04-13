
import os

class Entity:
    def __init__(self, name, possessive, hp, attack, defense, magic, mp, moves, inventory, spells):
        self.name = name
        self.possessive = possessive
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.attack_mod = 0
        self.defense = defense
        self.defense_mod = 0
        self.magic = magic
        self.magic_mod = 0
        self.mp = mp
        self.max_mp = mp
        self.moves = moves
        self.inventory = inventory
        self.spells = spells
        self.sleep_duration = 0
        self.sheep_duration = 0
        self.first_sheep = False
        self.statuses = []

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        damage = max(1, dmg)
        self.hp = max(0, self.hp - damage)
        return f"It did {damage} damage."

    def restore_hp(self, val):
        healed = min(self.max_hp, self.hp + val) - self.hp
        self.hp += healed
        return f"Restored {healed} HP."

    def restore_mp(self, val):
        healed = min(self.max_mp, self.mp + val) - self.mp
        self.mp += healed
        return f"Restored {healed} MP."

    def modify_attack(self, val):
        self.attack = self.attack + val
        self.attack_mod += val
        return f"Attack {'decreased' if val < 0 else 'increased'} by {val}."

    def modify_defense(self, val):
        self.defense = self.defense + val
        self.defense_mod += val
        return f"Defense {'decreased' if val < 0 else 'increased'} by {val}."
    
    def modify_magic(self, val):
        self.magic = self.magic + val
        self.magic_mod += val
        return f"Magic {'decreased' if val < 0 else 'increased'} by {val}."

    def get_status(self, name):
        for s in self.statuses:
            if s.name == name:
                return s
        return None
    
    def remove_status(self, name):
        self.statuses = [s for s in self.statuses if s.name != name]

class Player(Entity):
    def __init__(self, name="Hero", hp=100, max_hp=100, attack=15, defense=5, magic=25, mp=30, max_mp=30, special="", moves=["Slash", "Heavy Strike"], inventory=["Potion","Potion","Power Boost"], spells = []):
        super().__init__(name, "Your", max_hp, attack, defense, magic, max_mp, moves, inventory, spells)
        self.hp = hp
        self.mp = mp
        self.special = special
    
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
                if key in ["moves", "inventory", "spells"]:
                    data[key] = value.split(',') if value.strip() != "" else []
                    for i in range(len(data[key])):
                        data[key][i] = data[key][i].strip()
                elif key in ["hp", "max_hp", "attack", "defense", "magic", "mp", "max_mp"]:
                    data[key] = int(value.strip())
                else:
                    data[key] = value.strip()
            return data
        
class Enemy(Entity):
    def __init__(self, name, species, hp, attack, defense, magic = 0, mp = 0, moves = ["Scratch"], inventory = [], spells = []):
        super().__init__(name, f"Their", hp, attack, defense, magic, mp, moves, inventory, spells)
        self.species = species

def getCurrentDirectory():
    return os.path.dirname(os.path.realpath(__file__)) + "\\"
