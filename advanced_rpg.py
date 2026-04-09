import os
import platform
import pygame
import random
import sys
import copy

from entities import Enemy, Player

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
    def __init__(self, rect, text, callback, hover_text=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hover_text = hover_text
        self.hovered = False

    def draw(self, surface):
        button_color = (50, 50, 150)
        if self.hovered:
            button_color = (100, 100, 200)  # Highlight if hovered
        if self.text == "Special" or self.text in specials:
            button_color = (50, 150, 150)
        pygame.draw.rect(surface, button_color, self.rect)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()
    
    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

class EffectContext:
    def __init__(self, game, user, target=None):
        self.game = game
        self.user = user
        self.target = target

class BattleGame:
    def __init__(self):
        self.player = None
        self.characters = {
            "Hero": 1,
            "Wizard": 2,
            "Barbarian": 3,
            "Tank": 4,
            "Bard": 5,
            # "Dev": 6
        }
        self.selected_character = None
        self.in_character_select = True

        self.enemies = [
            Enemy("Goblin", 50, 10, 2, ["Bite", "Scratch", "Surprise"]),
            Enemy("Orc", 80, 12, 4),
            Enemy("Dragon", 150, 20, 8, ["Bite", "Fire Breath"]),
            Enemy("Elder Dragon", 300, 25, 10, ["Bite", "Greater Fire Breath"]),
            Enemy("Bandit", 60, 14, 3, ["Slash"], ["Potion", "Potion", "Potion", "Potion", "Potion"])
        ]

        self.moves = {
            "Slash": {
                "effect": ["damage"], 
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense + 5
            },
            "Heavy Strike": {
                "effect": ["damage"], 
                "damage": lambda ctx: (ctx.user.attack - ctx.target.defense) * 2 - 3
            },
            "Bite": {
                "effect": ["damage"], 
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense + 2
            },
            "Scratch": {
                "effect": ["damage"], 
                "damage": lambda ctx: ctx.user.attack - ctx.target.defense - 2
            },
            "Fire Breath": {
                "effect": ["damage"], 
                "damage": lambda ctx: 25 - ctx.target.defense
            },
            "Greater Fire Breath": {
                "effect": ["damage"], 
                "damage": lambda ctx: 30 - ctx.target.defense
            },
            "Surprise": {
                "effect": ["status"], 
                "func": lambda ctx: ctx.target.modify_defense(-2)
            }
        }
        self.spells = {
            "Fireball": {
                "effect": ["damage"], 
                "mp": 10, 
                "damage": lambda ctx: ctx.user.magic - ctx.target.defense + 5, 
                "hover": "Damage"
            },
            "Ice Spike": {
                "effect": ["damage"], 
                "mp": 8, 
                "damage": lambda ctx: ctx.user.magic - ctx.target.defense - 5, 
                "hover": "Damage"
            },
            "Lambda": {
                "effect": ["status"], 
                "mp": 5, 
                "func": lambda ctx: ctx.game.summon_sheep(), 
                "hover": "Summon a sheep to defend you"
            },
            "Magic Up": {
                "effect": ["status"], 
                "mp": 20, 
                "func": lambda ctx: ctx.user.modify_magic(10), 
                "hover": "+10 Magic"
            }
        }
        self.items = {
            "Potion": {
                "effect": ["status"],
                "func": lambda ctx: ctx.user.restore_hp(30), 
                "hover": "+30 HP"
            },
            "Mana Potion": {
                "effect": ["status"],
                "func": lambda ctx: ctx.user.restore_mp(20), 
                "hover": "+20 MP"
            },
            "Power Boost": {
                "effect": ["status"],
                "func": lambda ctx: ctx.user.modify_attack(5), 
                "hover": "+5 Attack"
            },
            "Magic Boost": {
                "effect": ["status"],
                "func": lambda ctx: ctx.user.modify_magic(10), 
                "hover": "+10 Magic"
            },
            "Dragon's Bane": {
                "effect": ["status"],
                "func": lambda ctx: ctx.game.kill_dragon(ctx), 
                "hover": "Kills a dragon"
            }
        }
        self.specials = {
            "Valor": {
                "effect": ["status"],
                "func": lambda ctx: ctx.game.valor(ctx.user)
            },
            "Rage": {
                "effect": ["status"],
                "func": lambda ctx: ctx.game.rage(ctx.user)
            },
            "Sheepda": {
                "effect": ["status"],
                "func": lambda ctx: ctx.game.sheepda(ctx.user)
            },
            "ArmorUp": {
                "effect": ["status"],
                "func": lambda ctx: ctx.game.armor_up(ctx.user)
            },
            "Sleep": {
                "effect": ["status"],
                "func": lambda ctx: ctx.game.sleep(ctx.target)
            },
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

    def minimize_window(self):
        pygame.display.iconify()
    
    def restore_window(self):
        if platform.system() == "Windows":
            try:
                import win32gui
                import win32con
                hwnd = pygame.display.get_wm_info()['window']
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

    def run_battle(self):
        self.restore_window()
        self.running = True
        
        while self.running:
            screen.fill((0, 0, 0))
            self.handle_events()
            self.render()
            self.logic()
            pygame.display.flip()
            clock.tick(60)

        self.minimize_window()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()  # <-- NEW
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            for button in self.buttons:
                button.handle_event(event)
        
        # Check for hover separately
        for button in self.buttons:
            button.check_hover(mouse_pos)

    def make_character_select_buttons(self):
        self.buttons.clear()
        for i, player in enumerate(self.characters.keys()):
            self.buttons.append(Button((300, 150 + i * 60, 200, 40), player, lambda p=player: self.select_character(self.characters[p])))

    def select_character(self, character):
        self.player = Player(**Player.load_player_from_file(character))
        self.in_character_select = False
        self.running = False

    def run_character_select(self):
        """
        Runs ONLY the character select screen.
        Blocks execution until a character is chosen.
        """
        self.in_character_select = True
        self.running = True
        self.make_character_select_buttons()

        while self.running:
            screen.fill((0, 0, 0))
            self.handle_events()
            self.render()
            pygame.display.flip()
            clock.tick(60)

        # after selection → hide window
        self.minimize_window()

        return self.player
    
    def make_buttons(self):
        ctx = EffectContext(self, self.player, self.enemy)
        self.buttons.clear()
        if self.turn != "player":
            return
        y_offset = 400
        spacing = 40
        if self.menu == "main":
            options = []
            if self.player.hp <= self.player.max_hp / 2 and not self.special_used:
                options.append(("Special", lambda: self.set_menu("special"), None))
            options.append(("Attack", lambda: self.set_menu("attack"), None))
            options.append(("Items", lambda: self.set_menu("items"), None))
            options.append(("Spells", lambda: self.set_menu("spells"), None))
            options.append(("Run", self.try_escape, None))

        elif self.menu == "attack":
            options = []
            for move_name in self.player.moves:
                move = self.moves[move_name]
                hover = ""
                if "damage" in move["effect"]:
                    base_damage = move["damage"](ctx)
                    min_damage = max(0, base_damage - 3)
                    max_damage = max(0, base_damage + 3)
                    hover += f"Damage: {min_damage}-{max_damage}"
                elif "status" in move["effect"]:
                    hover += "status move"
                options.append((move_name, lambda m=move_name: self.select_move(ctx, m), hover))
            options.append(("Back", self.go_back, None))
            
        elif self.menu == "spells":
            options = []
            for spell_name in self.spells.keys():
                spell = self.spells[spell_name]
                spell_mp = spell["mp"]
                hover = spell["hover"]
                if "damage" in spell["effect"]:
                    base_damage = spell["damage"](ctx)
                    min_damage = max(1, base_damage - 3)
                    max_damage = max(1, base_damage + 3)
                    hover = f"Damage: {min_damage}-{max_damage}"
                if self.player.mp >= spell_mp:
                    options.append((f"{spell_name} ({spell_mp} MP)", lambda s=spell_name: self.cast_spell(ctx, s), hover))
            options.append(("Back", self.go_back, None))
            
        elif self.menu == "items":
            items = list(set(self.player.inventory))
            options = [(f"{item} x{self.player.inventory.count(item)}", lambda i=item: self.use_item(ctx, i), self.items[item]["hover"]) for item in items]
            options.append(("Back", self.go_back, None))

        elif self.menu == "special":
            options = [
                (self.player.special, self.set_special, None),
                ("Back", self.go_back, None)
            ]
        
        else:
            return

        for i, (text, callback, hover) in enumerate(options):
            width = max(200, font.size(text)[0] + 20)
            self.buttons.append(Button((50, y_offset + i * spacing, width, 30), text, callback, hover))

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

    def select_move(self, ctx, move):
        self.selected_move = move
        self.action = "attack"
        self.make_buttons()

    def use_item(self, ctx, item_name):
        if item_name not in ctx.user.inventory:
            print("Item not in inventory:", item_name)
            return

        ctx.user.inventory.remove(item_name)

        article = "an" if item_name[0].lower() in "aeiou" else "a"

        result = self.items[item_name]["func"](ctx)
        
        self.last_player_action = f"You used {article} {item_name}! {result}"
        self.turn = "enemy"
        self.make_buttons()

    def cast_spell(self, ctx, spell_name):
        spell = self.spells[spell_name]
        if self.player.mp >= spell["mp"]:
            self.selected_move = spell_name
            self.action = "spell"
            ctx.user.mp -= spell["mp"]
        else:
            self.last_player_action = "Not enough MP!"
            self.turn = "enemy"
        self.make_buttons()

    def execute_ability(self, ability, ctx):
        effects = ability["effect"]
        result = ""
        for effect in effects:
            if effect == "damage":
                result += self.do_damage(ctx.target, ability["damage"](ctx))
                if ctx.target.sleep_duration:
                    ctx.target.sleep_duration = 0
                    self.last_enemy_action = "The enemy has awoken."
            if effect == "status":
                result += ability["func"](ctx)
        return result

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
            
        # Draw hover popup if hovering
        for button in self.buttons:
            if button.hovered and button.hover_text:
                popup_font = pygame.font.SysFont("arial", 18)
                popup_surface = popup_font.render(button.hover_text, True, (255, 255, 0))
                popup_rect = popup_surface.get_rect()
                popup_rect.topleft = (button.rect.right + 10, button.rect.top)
                screen.blit(popup_surface, popup_rect)

    def logic(self):
        if self.in_character_select:
            self.make_character_select_buttons()
            return

        if self.turn == "player" and self.action:
            ctx = EffectContext(self, self.player, self.enemy)
            self.last_player_action = ""
            self.last_enemy_action = ""
            self.victory_text = ""
            if self.action == "attack":
                move = self.moves[self.selected_move]
                result = self.execute_ability(move, ctx)
                self.last_player_action = f"You used {self.selected_move}! {result}"
            elif self.action == "spell":
                spell = self.spells[self.selected_move]
                result = self.execute_ability(spell, ctx)
                self.last_player_action = f"You cast {self.selected_move}! {result}"
            elif self.action == "special":
                special = self.specials[self.selected_move]
                result = self.execute_ability(special, ctx)
                self.last_player_action = f"You activated {self.selected_move}!"
                self.last_enemy_action = result
                
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
        ctx = EffectContext(self, self.enemy, self.player)
        if self.enemy.sleep_duration:
            self.enemy.sleep_duration -= 1
            if self.enemy.sleep_duration == 0:
                self.last_enemy_action == "The enemy has awoken."
        elif self.enemy.name == "Bandit" and self.enemy.hp < 20 and "Potion" in self.enemy.inventory:
            self.enemy.inventory.remove("Potion")
            result = self.items["Potion"]["func"](ctx)
            self.last_enemy_action = f"{self.enemy.name} used a Potion! {result}"
        else:
            move_name = random.choice(self.enemy.moves)
            if "status" in self.moves[move_name]["effect"]:
                message = self.moves[move_name]["func"](ctx)
                self.last_enemy_action = f"{self.enemy.name} used {move_name}! Your {message}!"
            elif self.sheep_block_active:
                self.last_enemy_action = f"{self.enemy.name}'s attack was blocked by the sheep!"
                self.sheep_block_active = False
                self.sheep_block_duration -= 1
                if self.enemy.name == "Dragon" and move_name == "Bite":
                    self.sheep_eaten_count += 1
            elif self.sheep_block_duration > 0:
                self.last_enemy_action = f"{self.enemy.name}'s attack was blocked by the sheep again!"
                self.sheep_block_duration -= 1
                if self.enemy.name == "Dragon" and move_name == "Bite":
                    self.sheep_eaten_count += 1
            else:
                move = self.moves[move_name]
                result = self.execute_ability(move, ctx)
                self.last_enemy_action = f"{self.enemy.name} used {move_name}! {result}"

        if "Dragon" in self.enemy.name and self.sheep_eaten_count >= 20:
            self.victory_text = f"The {self.enemy.name} gets full from eating sheep and flies away!"
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

    def do_damage(self, target, val):
        damage = max(1, damage_variance(val))
        return target.take_damage(damage)

    def kill_dragon(self, ctx):
        if ctx.target and "Dragon" in ctx.target.name:
            ctx.target.hp = 0
            ctx.game.last_enemy_action = "The Dragon falls dead."
            return ""
        return "But it had no effect."
    
    def summon_sheep(self, turns = 1):
        self.sheep_block_active = True
        if turns == 1:
            self.sheep_block_duration = random.randint(turns, turns + 1)
        else:
            self.sheep_block_duration = turns
        return "A sheep blocks the next attack!"
    
    def valor(self, user):
        user.modify_attack(5)
        user.modify_defense(5)
        return "Attack and Defense increase by 5."
    
    def rage(self, user):
        user.rage_active = True
        return "You now take half damage."
    
    def sheepda(self):
        self.summon_sheep(3)
        return "You summon a flock of sheep that goes away in 3 turns."
    
    def armor_up(self, user):
        user.hp += user.max_hp
        return "You fortify your armor."
    
    def sleep(self):
        self.sleep_duration = 3
        return "The enemy has fallen asleep."

if __name__ == "__main__":
    game = BattleGame()
    game.select_enemy("Goblin")
    game.run_battle()
    game.make_buttons()
    game.run_battle()
    pygame.quit()
    sys.exit()