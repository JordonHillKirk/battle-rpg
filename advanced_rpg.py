import os
import platform
import pygame
import random
import sys
import copy

def getCurrentDirectory():
    return os.path.dirname(os.path.realpath(__file__)) + "\\"

def restore_window():
    if platform.system() == "Windows":
        try:
            import win32gui
            import win32con
            hwnd = pygame.display.get_wm_info()['window']
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except ImportError:
            print("pywin32 is not installed. Cannot restore window on Windows.")
        except Exception as e:
            print(f"Error restoring window: {e}")
    else:
        print("Window restore is not supported on this platform.")


# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Battle Game")
font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()
character_path = getCurrentDirectory()

sheep_image = pygame.Surface((80, 80))
sheep_image.fill((255, 255, 255))
pygame.draw.circle(sheep_image, (200, 200, 200), (40, 40), 40)

specials = ["Rage", "Valor", "Sheepda", "ArmorUp", "Sleep"]

def draw_text(surface, text, x, y, color=(255,255,255)):
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))

def draw_status(surface, entity, x, y):
    draw_text(surface, f"{entity.name}", x, y)
    draw_text(surface, f"HP: {entity.hp}/{entity.max_hp}", x, y + 30)
    if hasattr(entity, 'mp'):
        draw_text(surface, f"MP: {entity.mp}/{entity.max_mp}", x, y + 60)

def damage_variance(damage):
    return random.randint(max(0, damage - 3), max(0, damage + 3))

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback

    def draw(self, surface):
        button_color = (50, 50, 150)
        if self.text == "Special" or self.text in specials:
            button_color = (50, 150, 150)
        pygame.draw.rect(surface, button_color, self.rect)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

class Entity:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

class Player(Entity):
    def __init__(self, name="Hero", hp=100, max_hp=100, attack=15, defense=5, magic=25, mp=30, max_mp=30, special="", inventory=["Potion","Potion","Power Boost"]):
        super().__init__(name, hp, attack, defense)
        self.max_hp = max_hp
        self.magic = magic
        self.mp = mp
        self.max_mp = max_mp
        self.special = special
        self.inventory = inventory
    
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
    def __init__(self, name, hp, attack, defense, special_moves=None):
        super().__init__(name, hp, attack, defense)
        self.special_moves = special_moves or {}
        self.inventory = []

class BattleGame:
    def __init__(self):
        self.characters = {
            "Hero": 1,
            "Wizard": 2,
            "Barbarian": 3,
            "Tank": 4,
            "Bard": 5
        }
        self.selected_character = None
        self.in_character_select = True

        bandit = Enemy("Bandit", 60, 14, 3)
        bandit.inventory = ["Potion"]
        self.enemies = [
            Enemy("Goblin", 50, 10, 2),
            Enemy("Orc", 80, 12, 4),
            Enemy("Dragon", 150, 20, 8, {"Fire Breath": 25}),
            bandit
        ]

        self.moves = {
            "Slash": lambda atk: atk + 5,
            "Heavy Slash": lambda atk: atk * 2 - 3
        }
        self.spells = {
            "Fireball": {"mp": 10, "damage": lambda magic: max(0, magic) + 5},
            "Ice Spike": {"mp": 8, "damage": lambda magic: max(0, magic - 5)},
            "Lambda": {"mp": 5, "effect": "summon_sheep"},
            "Magic Up": {"mp": 20, "boost": 15}
        }
        self.items = {
            "Potion": {"heal": 20},
            "Power Boost": {"boost": 5},
            "Dragon's Bane": {"kill dragon": True}
        }
        self.battle_prep()

    def battle_prep(self, e = None):
        self.turn = "player"
        self.action = None
        self.selected_move = None
        self.menu = "main"
        self.menu_stack = []
        self.sheep_block_active = False
        self.sheep_block_duration = 0
        self.sheep_eaten_count = 0
        self.sleep_duration = 0
        self.select_enemy(e)
        self.running = True
        self.last_player_action = ""
        self.last_enemy_action = ""
        self.victory_text = ""
        self.buttons = []
        self.special_active = False
        self.special_turn_count = 0
        self.special_used = False
        self.ran_away = False

    def select_enemy(self, e = None):
        self.enemy = random.choice(self.enemies)
        if e:
            for en in self.enemies:
                if en.name == e:
                    self.enemy = copy.deepcopy(en)
            if self.enemy == None:
                self.enemy = copy.deepcopy(random.choice(self.enemies))
        else:
            self.enemy = copy.deepcopy(random.choice(self.enemies))

    def run(self):
        self.running = True
        restore_window()
        while self.running:
            screen.fill((0, 0, 0))
            self.handle_events()
            self.render()
            self.logic()
            pygame.display.flip()
            clock.tick(60)
        pygame.display.iconify()
        

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for button in self.buttons:
                button.handle_event(event)

    def make_character_select_buttons(self):
        self.buttons.clear()
        for i, player in enumerate(self.characters.keys()):
            self.buttons.append(Button((300, 150 + i * 60, 200, 40), player, lambda p=player: self.select_character(self.characters[p])))

    def select_character(self, character):
        self.player = Player(**Player.load_player_from_file(character))
        self.in_character_select = False
        self.running = False
        self.make_buttons()

    def make_buttons(self):
        self.buttons.clear()
        if self.turn != "player":
            return
        y_offset = 400
        spacing = 40
        if self.menu == "main":
            options = []
            if self.player.hp <= self.player.max_hp / 2 and not self.special_used:
                options.append(("Special", lambda: self.set_menu("special")))
            options.append(("Attack", lambda: self.set_menu("attack")))
            options.append(("Items", lambda: self.set_menu("items")))
            options.append(("Spells", lambda: self.set_menu("spells")))
            options.append(("Run", self.try_escape))

        elif self.menu == "attack":
            options = []
            for move in self.moves.keys():
                options.append((move, lambda m=move: self.select_move(m)))
            options.append(("Back", self.go_back))
            
        elif self.menu == "spells":
            options = []
            for spell in self.spells.keys():
                spell_mp = self.spells[spell]["mp"]
                if self.player.mp >= spell_mp:
                    options.append((f"{spell} ({spell_mp} MP)", lambda s=spell: self.cast_spell(s)))
            options.append(("Back", self.go_back))
            
        elif self.menu == "items":
            items = list(set(self.player.inventory))
            options = [(f"{item} x{self.player.inventory.count(item)}", lambda i=item: self.use_item(i)) for item in items]
            options.append(("Back", self.go_back))

        elif self.menu == "special":
            options = [
                (self.player.special, self.set_special),
                ("Back", self.go_back)
            ]
        
        else:
            return

        for i, (text, callback) in enumerate(options):
            width = max(200, font.size(text)[0] + 20)
            self.buttons.append(Button((50, y_offset + i * spacing, width, 30), text, callback))

    def set_menu(self, menu):
        self.menu = menu
        if self.turn == "player":
            self.make_buttons()

    def go_back(self):
        self.menu = "main"
        if self.turn == "player":
            self.make_buttons()

    def set_special(self):
        if self.player.special != "ArmorUp" and self.player.special != "Sleep":
            self.special_active = True
            self.special_turn_count = 3
        self.special_used = True
        self.action = "special"
        self.selected_move = self.player.special
        self.menu = "main"
        self.make_buttons()

    def try_escape(self):
        self.last_enemy_action = ""
        self.last_player_action = "You escaped!" if random.random() < 0.5 else "Failed to escape!"
        if self.last_player_action == "You escaped!":
            self.ran_away = True
            pygame.time.delay(1000)
            self.running = False
        else:
            self.turn = "enemy"
        self.make_buttons()

    def select_move(self, move):
        self.selected_move = move
        self.action = "attack"
        self.make_buttons()

    def cast_spell(self, spell_name):
        spell = self.spells[spell_name]
        if self.player.mp >= spell["mp"]:
            self.selected_move = spell_name
            self.action = "spell"
        else:
            self.last_player_action = "Not enough MP!"
            self.turn = "enemy"
        self.make_buttons()

    def use_item(self, item_name):
        if item_name in self.player.inventory:
            self.player.inventory.remove(item_name)
            if item_name == "Potion":
                heal = self.items[item_name]["heal"]
                self.player.hp = min(self.player.max_hp, self.player.hp + heal)
                self.last_player_action = f"You used a Potion! Restored {heal} HP."
            elif item_name == "Power Boost":
                self.player.attack += self.items[item_name]["boost"]
                self.last_player_action = "You used a Power Boost! Attack increased."
            elif item_name == "Dragon's Bane":
                if self.enemy.name == "Dragon":
                    self.enemy.hp = 0
                    self.last_player_action = "You used the Dragon's Bane!"
                    self.last_enemy_action = "The Dragon falls dead."
                else:
                    self.last_player_action = "You used the Dragon's Bane...but it does nothing."

            self.turn = "enemy"
            self.make_buttons()

    def render(self):
        if self.in_character_select:
            draw_text(screen, "Choose your character:", 300, 80)
        else:
            draw_status(screen, self.player, 50, 50)
            draw_status(screen, self.enemy, 500, 50) 
            y = 140
            if self.sleep_duration:
                draw_text(screen, "Asleep", 500, y, (200, 50, 50))
            if self.special_active:
                draw_text(screen, f"{self.player.special} is active", 50, y, (200, 255, 200))
                y += 30
            if self.sheep_block_duration:
                draw_text(screen, "Sheep will block next attack!", 50, y, (200, 255, 200))
            if self.last_player_action:
                draw_text(screen, self.last_player_action, 300, 460)
            if self.last_enemy_action:
                draw_text(screen, self.last_enemy_action, 300, 490)
            if self.victory_text:
                draw_text(screen, self.victory_text, 300, 520)
        for button in self.buttons:
            button.draw(screen)

    def logic(self):
        if self.in_character_select:
            self.make_character_select_buttons()
            return

        if self.turn == "player" and self.action:
            self.last_player_action = ""
            self.last_enemy_action = ""
            self.victory_text = ""
            if self.action == "attack":
                move_func = self.moves[self.selected_move]
                damage = max(1, damage_variance(move_func(self.player.attack - self.enemy.defense)))
                self.enemy.take_damage(damage)
                if self.sleep_duration:
                    self.sleep_duration = 0
                    self.last_enemy_action = "The enemy has awoken."
                self.last_player_action = f"You used {self.selected_move} for {damage} damage!"
            elif self.action == "spell":
                spell = self.spells[self.selected_move]
                self.player.mp -= spell["mp"]
                if "damage" in spell:
                    damage = max(1, damage_variance(spell["damage"](self.player.magic - self.enemy.defense)))
                    self.enemy.take_damage(damage)
                    if self.sleep_duration:
                        self.sleep_duration = 0
                        self.last_enemy_action = "The enemy has awoken."
                    self.last_player_action = f"You cast {self.selected_move} for {damage} damage!"
                elif "boost" in spell:
                    self.player.magic += spell["boost"]
                    self.last_player_action = f"You cast {self.selected_move} boosting Magic by {spell["boost"]}."
                elif spell.get("effect") == "summon_sheep":
                    self.sheep_block_active = True
                    self.sheep_block_duration = random.randint(1, 2)
                    self.last_player_action = "You cast Lambda! A sheep blocks the next attack!"
            elif self.action == "special":
                self.last_player_action = f"You activated {self.selected_move}!"
                if self.selected_move == "Valor":
                    self.player.attack += 5
                    self.player.defense += 5
                    self.last_enemy_action = "Your Attack and Defense increase by 5."
                if self.selected_move == "Rage":
                    self.last_enemy_action = "You now take half damage."
                if self.selected_move == "Sheepda":
                    self.sheep_block_active = True
                    self.sheep_block_duration = 3
                    self.last_enemy_action = "You summon a flock of sheep that goes away in 3 turns."
                if self.selected_move == "ArmorUp":
                    self.player.hp += self.player.max_hp
                    self.last_enemy_action = "You fortify your armor."
                if self.selected_move == "Sleep":
                    self.last_enemy_action = "The enemy has fallen asleep."
                    self.sleep_duration = 3
                self.action = None
                self.selected_move = None
                self.set_menu("main")
                return
            self.action = None
            self.selected_move = None
            self.set_menu("")
            self.turn = "enemy"
        elif self.turn == "enemy" and self.enemy.is_alive():
            self.enemy_turn()
            self.set_menu("main")
        
        
        if not self.player.is_alive():
            self.victory_text = "You were defeated!"
            self.buttons = [Button((50, 400, 200, 30), "Quit", self.quit_game)]
            self.turn = ""

        if not self.enemy.is_alive():
            self.victory_text = f"You defeated the {self.enemy.name}!"
            self.buttons = [Button((50, 400, 200, 30), "Quit", self.quit_game)]

    def quit_game(self):
        self.running = False

    def enemy_turn(self):
        if self.sleep_duration:
            self.sleep_duration -= 1
            if self.sleep_duration == 0:
                self.last_enemy_action == "The enemy has awoken."
        elif self.enemy.name == "Bandit" and self.enemy.hp < 20 and "Potion" in self.enemy.inventory:
            # self.enemy.inventory.remove("Potion")
            heal = 30
            self.enemy.hp = min(self.enemy.max_hp, self.enemy.hp + heal)
            self.last_enemy_action = f"{self.enemy.name} used a Potion! Restored {heal} HP."
        else:
            move = random.choice(["Bite", "Scratch"])
            if self.enemy.name == "Dragon":
                move = random.choice(["Bite", "Fire Breath"])
            power = self.enemy.attack + 2 if move == "Bite" else self.enemy.attack - 2
            if move == "Fire Breath":
                power = 25

            if self.sheep_block_active:
                self.last_enemy_action = f"{self.enemy.name}'s attack was blocked by the sheep!"
                self.sheep_block_active = False
                self.sheep_block_duration -= 1
                if self.enemy.name == "Dragon" and move == "Bite":
                    self.sheep_eaten_count += 1
            elif self.sheep_block_duration > 0:
                self.last_enemy_action = f"{self.enemy.name}'s attack was blocked by the sheep again!"
                self.sheep_block_duration -= 1
                if self.enemy.name == "Dragon" and move == "Bite":
                    self.sheep_eaten_count += 1
            else:
                damage = max(1, damage_variance(power - self.player.defense))
                if self.special_active and self.player.special == "Rage":
                    damage = damage // 2
                self.player.take_damage(damage)
                self.last_enemy_action = f"{self.enemy.name} used {move}! You took {damage} damage!"

        if self.enemy.name == "Dragon" and self.sheep_eaten_count >= 20:
            self.victory_text = "The Dragon gets full from eating sheep and flies away!"
            self.buttons = [Button((300, 580, 200, 30), "Quit", self.quit_game)]

        if self.special_active:
            self.special_turn_count -= 1
            if self.special_turn_count <= 0:
                self.special_active = False
                if self.player.special != "ArmorUp":
                    self.victory_text = f"Your {self.player.special} ability has worn off."
                if self.player.special == "Valor":
                    self.player.attack -= 5
                    self.player.defense -= 5

        pygame.display.flip()
        pygame.time.delay(1000)
        self.player.mp = min(self.player.max_mp, self.player.mp + 1)
        self.turn = "player"
        self.make_buttons()

if __name__ == "__main__":
    game = BattleGame()
    game.select_enemy("Dragon")
    game.run()
    game.run()
    pygame.quit()
    sys.exit()