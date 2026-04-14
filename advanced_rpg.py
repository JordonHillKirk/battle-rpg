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
    if entity.max_mp > 0:
        draw_text(surface, f"MP: {entity.mp}/{entity.max_mp}", x, y + 60)
    y += 60
    for status in entity.statuses:
        if status.data.get("display_text", None):
            y += 30
            draw_text(surface, status.data["display_text"], x, y, (200, 255, 200))

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
    
class Status:
    def __init__(self, name, duration, handlers = {}, data = {}):
        self.name = name
        self.duration = duration
        self.handlers = handlers
        self.data = data

    def reduce_duration(self, val):
        self.duration -= val
        if self.duration <= 0:
            if self.handlers.get("on_0_duration", None):
                self.handlers["on_0_duration"]()


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
            Enemy("Goblin", "Goblin", 50, 10, 2, 0, 0, ["Bite", "Scratch", "Surprise"]),
            Enemy("Orc", "Orc", 80, 12, 4),
            Enemy("Orc Shaman", "Orc", 60, 14, 3, 20, 20, ["Slash"], [], ["Lambda"]),
            Enemy("Dragon", "Dragon", 150, 20, 8, 0, 0, ["Bite", "Fire Breath"]),
            Enemy("Elder Dragon", "Dragon", 300, 25, 10, 0, 0, ["Bite", "Greater Fire Breath"]),
            Enemy("Bandit", "Human", 60, 14, 3, 0, 0, ["Slash"], ["Potion", "Potion", "Potion", "Potion", "Potion"]),
        ]

        self.abilities = {
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
            },
            "Fireball": {
                "effect": ["damage"], 
                "cost": {
                    "mp": 10, 
                },
                "damage": lambda ctx: ctx.user.magic - ctx.target.defense + 5, 
                "hover": "Damage"
            },
            "Ice Spike": {
                "effect": ["damage"], 
                "cost": {
                    "mp": 8, 
                },
                "damage": lambda ctx: ctx.user.magic - ctx.target.defense - 5, 
                "hover": "Damage"
            },
            "Lambda": {
                "effect": ["status"], 
                "cost": {
                    "mp": 5, 
                }, 
                "func": lambda ctx: ctx.game.summon_sheep(ctx.user), 
                "hover": "Summon a sheep to defend you"
            },
            "Magic Up": {
                "effect": ["status"], 
                "cost": {
                    "mp": 20, 
                },
                "func": lambda ctx: ctx.user.modify_magic(10), 
                "hover": "+10 Magic"
            },
            "Potion": {
                "effect": ["heal"], 
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.user.restore_hp(30), 
                "hover": "+30 HP",
                "value": 30
            },
            "Mana Potion": {
                "effect": ["status"],
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.user.restore_mp(20), 
                "hover": "+20 MP"
            },
            "Power Boost": {
                "effect": ["status"],
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.user.modify_attack(5), 
                "hover": "+5 Attack"
            },
            "Magic Boost": {
                "effect": ["status"],
                "cost": {
                    "item": 1, 
                },
                "func": lambda ctx: ctx.user.modify_magic(10), 
                "hover": "+10 Magic"
            },
            "Dragon's Bane": {
                "effect": ["status"],
                "cost": {
                    "item": 1,
                },
                "func": lambda ctx: ctx.game.kill_dragon(ctx), 
                "hover": "Kills a dragon"
            }, 
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

        self.text_formatter = {
            "attack": {"verb": "used"},
            "item": {"verb": "used", "article": lambda name: "an " if name[0] in "aeiou" else "a "},
            "spell": {"verb": "cast"},
            "special": {"verb": "activated"}
        }

        self.battle_prep()

    def battle_prep(self, e = None):
        self.turn = "player"
        self.action = None
        self.selected_move = None
        self.menu = "main"
        self.menu_stack = []
        self.select_enemy(e)
        self.running = True
        self.buttons = []
        self.special_active = False
        self.special_turn_count = 0
        self.dragon_full = False
        self.ran_away = False
        if hasattr(self.player, "special_used"):
            self.player.special_used = False
        if hasattr(self.player, "sheep_duration") and self.player.sheep_duration:
            self.player.first_sheep = True
        self.combat_log = []
        self.log_offset = 0  # for scrolling
        self.max_log_lines = 4
        self.pending_logs = []

    def log(self, message):
        self.combat_log.append(message)

        # Optional: limit size
        if len(self.combat_log) > 100:
            self.combat_log.pop(0)

        # Auto-scroll to bottom
        self.log_offset = 0

    def draw_combat_log(self, surface):
        x = 300
        y = 400
        line_height = 30

        visible_lines = self.max_log_lines
        start = max(0, len(self.combat_log) - visible_lines - self.log_offset)
        end = start + visible_lines

        lines = self.combat_log[start:end]

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (255, 255, 255))
            surface.blit(text_surface, (x, y + i * line_height))

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
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # scroll up
                    self.log_offset = min(self.log_offset + 1, len(self.combat_log))
                elif event.button == 5:  # scroll down
                    self.log_offset = max(self.log_offset - 1, 0)
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
            if self.player.hp <= self.player.max_hp / 2 and not self.player.special_used:
                options.append(("Special", lambda: self.set_menu("special"), None))
            options.append(("Attack", lambda: self.set_menu("attack"), None))
            options.append(("Items", lambda: self.set_menu("items"), None))
            options.append(("Spells", lambda: self.set_menu("spells"), None))
            options.append(("Run", self.try_escape, None))

        elif self.menu == "attack":
            options = []
            for move_name in self.player.moves:
                move = self.abilities[move_name]
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
            for spell_name in self.player.spells:
                spell = self.abilities[spell_name]
                spell_mp = spell.get("cost", {}).get("mp", 0)
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
            options = [(f"{item} x{self.player.inventory.count(item)}", lambda i=item: self.use_item(ctx, i), self.abilities[item]["hover"]) for item in items]
            options.append(("Back", self.go_back, None))

        elif self.menu == "special":
            options = [
                (self.player.special, self.set_special, None),
                ("Back", self.go_back, None)
            ]

        elif self.menu == "quit":
            options = [("Quit", self.quit_game, None)]
        
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
        self.set_menu("main")

    def set_special(self):
        self.player.special_used = True
        self.action = "special"
        self.selected_move = self.player.special
        self.set_menu("main")

    def try_escape(self):
        chance = .5
        if random.random() < chance:
            self.log("You escaped!")
            self.ran_away = True
            pygame.time.delay(1000)
            self.running = False
        else:
            self.log("You failed to escape!")
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
        self.selected_move = item_name
        self.action = "item"
        self.make_buttons()

    def cast_spell(self, ctx, spell_name):
        spell = self.abilities[spell_name]
        if self.player.mp >= spell["cost"]["mp"]:
            self.selected_move = spell_name
            self.action = "spell"
        else:
            self.log("Not enough MP!")
            self.turn = "enemy"
        self.make_buttons()

    def execute_ability(self, ctx, ability, ability_name):
        effects = ability["effect"]
        
        self.pay_ability_costs(ctx.user, ability, ability_name)

        for effect in effects:
            if effect == "damage":
                ctx.ability_name = ability_name
                
                pre = self.apply_pre_damage(ctx)

                if pre["blocked"]:
                    return
                
                damage = ability["damage"](ctx)
                self.log(self.do_damage(ctx.target, damage))

                if ctx.target.sleep_duration:
                    ctx.target.sleep_duration = 0
                    self.log("The enemy has awoken.")

            if effect in ["status", "heal"]:
                self.log(ability["func"](ctx))

    def get_ability(self):
        return self.abilities[self.selected_move]

    def pay_ability_costs(self, user, ability, ability_name):
        cost = ability.get("cost", {})

        # Cost
        user.mp -= cost.get("mp", 0)
        for _ in range(cost.get("item", 0)):
            user.inventory.remove(ability_name)

    def render(self):
        if self.in_character_select:
            draw_text(screen, "Choose your character:", 300, 80)
        else:
            draw_status(screen, self.player, 50, 50)
            draw_status(screen, self.enemy, 500, 50) 

            self.draw_combat_log(screen)

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
            self.player_turn()
            self.set_menu("")
            self.change_turn("enemy")
            
        elif self.turn == "enemy" and self.enemy.is_alive():
            self.enemy_turn()
            self.end_of_round()
            self.change_turn("player")
            self.set_menu("main")
        
        if not self.player.is_alive():
            self.victory_text = "You were defeated!"
            self.end_battle()

        if not self.enemy.is_alive():
            self.victory_text = f"You defeated the {self.enemy.name}!"
            self.end_battle()
        
        if hasattr(self, "dragon_full") and self.dragon_full:
            self.victory_text = f"The {self.enemy.name} gets full from eating sheep and flies away!"
            self.end_battle()

    def end_battle(self):
        self.turn = "player"
        self.set_menu("quit")

    def quit_game(self):
        self.running = False

    def change_turn(self, p):
        self.turn = p
        self.start_of_turn(getattr(self, p, "error"))

    def player_turn(self):
        ctx = EffectContext(self, self.player, self.enemy)

        ability = self.get_ability()
        verb = self.text_formatter[self.action]["verb"]
        article = self.text_formatter[self.action].get("article", "")
        if article != "":
            article = article(self.selected_move)

        self.log(f"You {verb} {article}{self.selected_move}!")
        self.execute_ability(ctx, ability, self.selected_move)

        self.action = ""
        self.selected_move = ""

        if self.action == "special":
            self.set_menu("main")

    def enemy_turn(self):
        ctx = EffectContext(self, self.enemy, self.player)
        if self.enemy.sleep_duration:
            self.enemy.sleep_duration -= 1
            if self.enemy.sleep_duration == 0:
                self.log("The enemy has awoken.")
        elif self.enemy.hp < 20 and "Potion" in self.enemy.inventory:
            self.enemy.inventory.remove("Potion")
            result = self.abilities["Potion"]["func"](ctx)
            self.log(f"{self.enemy.name} used a Potion! {result}")
        else:
            abilities = self.get_usable_enemy_abilities(self.enemy)

            if not abilities:
                self.log("The enemy hesitates...")
                return

            ability_type, ability_name = random.choice(abilities)
            ability = self.abilities[ability_name]

            verb = self.text_formatter[ability_type]["verb"] 
            self.log(f"{self.enemy.name} {verb} {ability_name}!")
            result = self.execute_ability(ctx, ability, ability_name)
                

    def get_enemy_abilities(self, enemy):
        abilities = []

        for move in enemy.moves:
            abilities.append(("attack", move))

        for item in enemy.inventory:
            abilities.append(("item", item))

        for spell in enemy.spells:
            abilities.append(("spell", spell))

        return abilities

    def get_usable_enemy_abilities(self, enemy):
        abilities = list(set(self.get_enemy_abilities(enemy)))
        usable = []

        for ability_type, name in abilities:
            ability = self.abilities[name]

            cost = ability.get("cost", {})
            if "mp" in cost and enemy.mp < cost["mp"]:
                continue
            if "item" in cost and enemy.inventory.count(name) < cost["item"]:
                continue

            # healing filter
            if "heal" in ability.get("effect", []):
                missing_hp = enemy.max_hp - enemy.hp
                if missing_hp <= ability.get("value", 0): 
                    continue

            usable.append((ability_type, name))
            
        return usable

    def start_of_turn(self, entity):
        self.handle_regen(entity)
        if self.special_active:
            self.special_turn_count -= 1
            if self.special_turn_count <= 0:
                self.special_active = False
                if self.player.special != "ArmorUp":
                    self.victory_text = f"Your {self.player.special} ability has worn off."
                if self.player.special == "Valor":
                    self.player.attack -= 5
                    self.player.defense -= 5

    def end_of_turn(self, entity):
        # self.apply_status_effects()
        # self.tick_durations()
        pass

    def end_of_round(self):
        pygame.display.flip()
        pygame.time.delay(1000)

    def apply_pre_damage(self, ctx):
        result = {
            "blocked": False,
            "end_battle": False
        }

        for status in list(ctx.target.statuses):  # copy for safe removal
            handler = status.handlers.get("on_pre_damage")

            if handler:
                effect_result = handler(ctx, status)

                if effect_result:
                    result.update(effect_result)

                # Stop early if blocked
                if result["blocked"]:
                    break

        return result

    def handle_regen(self, entity): 
        entity.restore_mp(1)
        if getattr(entity, "speedy_mp_recovery", False):
            entity.restore_mp(1)

    def do_damage(self, target, val):
        damage = max(1, damage_variance(val))
        return target.take_damage(damage)

    def kill_dragon(self, ctx):
        if ctx.target and "Dragon" in ctx.target.name:
            ctx.target.hp = 0
            ctx.game.log("The Dragon falls dead.")
            return ""
        return "But it had no effect."
    
    def summon_sheep(self, user, turns = 1):
        if turns == 1:
            duration = random.randint(turns, turns + 1)
        else:
            duration = turns
        handlers = {
            "on_pre_damage": self.handle_sheep,
            "on_0_duration": lambda: self.pending_logs.append("The sheep disappeared.")
        }
        data = {
            "display_text": "Sheep will block next attack!",
            "first_sheep": True
        }
        status = Status("Sheep", duration, handlers, data)
        user.statuses.append(status)
        self.log("A sheep blocks the next attack!")
    
    def sheep_pre_damage(self, ctx):
        status = ctx.target.get_status("Sheep")
        if status != None:
            return False
        
        attacker = ctx.user
        
        if getattr(attacker, "species", None) == "Dragon" and ctx.ability_name == "Bite":
            self.log(f"{attacker.name} takes a bite of sheep.")
            attacker.sheep_eaten = getattr(attacker, "sheep_eaten", 0) + 1
            if attacker.sheep_eaten >= 10:
                self.dragon_full = True
        else:
            result = f"But, a sheep blocked the attack"
            if status.data["first_sheep"]:
                status.data["first_sheep"] = False
            else:
                result += " again"
            result += "."
            self.log(result)

        status.reduce_duration(1)
        return {"blocked": True}

    def valor(self, user):
        user.modify_attack(5)
        user.modify_defense(5)
        return "Attack and Defense increase by 5."
    
    def rage(self, user):
        user.rage_active = True
        return "You now take half damage."
    
    def sheepda(self, user):
        self.summon_sheep(user, 3)
        return "You summon a flock of sheep that goes away in 3 turns."
    
    def armor_up(self, user):
        user.hp += user.max_hp
        return "You fortify your armor."
    
    def sleep(self, target, turns = 1):
        if turns == 1:
            duration = random.randint(turns, turns + 1)
        else:
            duration = turns
        handlers = {"on_turn_start": self.snooze, "on_0_duration": lambda: self.log(f"{target.name} woke up")}
        data = {"display_text": "Sheep will block next attack!", "first_sheep": True}
        status = Status("Sheep", duration, handlers, data)
        target.statuses.append(status)
        return "The enemy has fallen asleep."
    
    def snooze(self, ctx):
        status = ctx.user.get_status("Sleep")

if __name__ == "__main__":
    game = BattleGame()
    game.select_enemy("Goblin")
    game.run_battle()
    game.make_buttons()
    game.run_battle()
    pygame.quit()
    sys.exit()