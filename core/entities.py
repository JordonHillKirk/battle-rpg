
import os

from core.constants import *
from core.status import Status

class Entity:
    def __init__(self, name, pronouns, hp, attack, defense, magic, mp, moves, inventory, spells):
        self.name = name
        self.pronouns = pronouns
        self.hp = hp
        self.max_hp = hp
        self.base_attack = attack
        self.base_defense = defense
        self.base_magic = magic
        self.mp = mp
        self.max_mp = mp
        self.moves = moves
        self.inventory = inventory
        self.spells = spells
        self.special_used = False
        self.sleep_duration = 0
        self.statuses = []

    @property
    def attack(self):
        return self.base_attack + sum(
            s.data.get(ATTACK, 0)
            for s in self.statuses
            if s.duration != 0
        )

    @property
    def defense(self):
        return self.base_defense + sum(
            s.data.get(DEFENSE, 0)
            for s in self.statuses
            if s.duration != 0
        )

    @property
    def magic(self):
        return self.base_magic + sum(
            s.data.get(MAGIC, 0)
            for s in self.statuses
            if s.duration != 0
        )

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        damage = max(1, dmg)
        self.hp = max(0, self.hp - damage)
        return f"It did {damage} damage."

    def restore_hp(self, val):
        healed = min(self.max_hp, self.hp + val) - self.hp
        self.hp += healed
        return f"{self.pronouns[PRONOUN_SUBJECT]} restored {healed} HP."

    def restore_mp(self, val):
        healed = min(self.max_mp, self.mp + val) - self.mp
        self.mp += healed
        return f"{self.pronouns[PRONOUN_SUBJECT]} restored {healed} MP."

    def modify_attack(self, val):
        self.base_attack = self.base_attack + val
        return f"{self.pronouns[PRONOUN_POSSESSIVE]} Attack {'decreased' if val < 0 else 'increased'} by {val}."

    def modify_defense(self, val):
        self.base_defense = self.base_defense + val
        return f"{self.pronouns[PRONOUN_POSSESSIVE]} Defense {'decreased' if val < 0 else 'increased'} by {val}."
    
    def modify_magic(self, val):
        self.base_magic = self.base_magic + val
        return f"{self.pronouns[PRONOUN_POSSESSIVE]} Magic {'decreased' if val < 0 else 'increased'} by {val}."

    def get_status(self, id):
        for s in self.statuses:
            if s.id == id:
                return s
        return None
    
    def add_status(self, status):
        if not isinstance(status, Status):
            raise TypeError(f"Expected Status, got {type(status)}")

        self.statuses.append(status)

    def remove_status(self, id):
        self.statuses = [s for s in self.statuses if s.id != id]

class Player(Entity):
    def __init__(self, name="Hero", hp=100, max_hp=100, attack=15, defense=5, magic=25, mp=30, max_mp=30, special="", moves=["slash", "heavy_strike"], inventory=["potion", "potion", "power_boost"], spells = []):
        super().__init__(name, {PRONOUN_SUBJECT: "You", PRONOUN_OBJECT: "you", PRONOUN_POSSESSIVE: "Your"}, max_hp, attack, defense, magic, max_mp, moves, inventory, spells)
        self.hp = hp
        self.mp = mp
        self.special = special
        
class Enemy(Entity):
    def __init__(self, name, species, hp, attack, defense, magic = 0, mp = 0, moves = ["scratch"], inventory = [], spells = []):
        super().__init__(name, {PRONOUN_SUBJECT: "They", PRONOUN_OBJECT: "them", PRONOUN_POSSESSIVE: "Their"}, hp, attack, defense, magic, mp, moves, inventory, spells)
        self.species = species
