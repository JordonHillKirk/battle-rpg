from math import floor
import os
import platform
import pygame
import random
import sys
import copy

from core.effect_context import EffectContext
from core.status import Status
from core.entities import Enemy, Player
from core.abilities import abilities
from core.constants import *

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

specials = ["Rage", "Valor", "Sheepda", "ArmorUp", "Sleep", "Superior Poison"]

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
        if status.data.get("display_text", None) and status.duration != 0:
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

class BattleGame:
    def __init__(self):
        self.player = None
        self.selected_character = None
        self.in_character_select = True

        self.enemies = [
            Enemy("Goblin", "Goblin", 50, 10, 2, 0, 0, ["bite", "scratch", "surprise"]),
            Enemy("Orc", "Orc", 80, 12, 4, 0, 0, ["slash"], [], []),
            Enemy("Orc Shaman", "Orc", 60, 14, 3, 20, 20, ["slash"], [], ["lambda"]),
            Enemy("Orc Elite", "Orc", 100, 15, 5, 10, 10, ["heavy_strike"], [], []),
            Enemy("Orc Champion", "Orc", 120, 18, 6, 20, 20, ["heavy_strike"], [], ["lambda"]),
            Enemy("Sneaky Orc", "Orc", 100, 15, 3, 0, 0, ["poison_blade"], [], []),
            Enemy("Dragon", "Dragon", 200, 20, 8, 0, 0, ["bite", "fire_breath"]),
            Enemy("Elder Dragon", "Dragon", 400, 25, 10, 0, 0, ["bite", "greater_fire_breath"]),
            Enemy("Bandit", "Human", 60, 14, 3, 0, 0, ["slash"], ["potion", "potion", "potion", "potion", "potion"]),
        ]

        self.abilities = abilities

        self.status_defs = {
            "stats_up": lambda: Status(
                "stats_up",
                "Stats Up",
                1,
                {},
                {
                    ATTACK: 0,
                    DEFENSE: 0,
                    MAGIC: 0,
                },
                {BUFF}
            ),
            "stats_down": lambda: Status(
                "stats_down",
                "Stats Down",
                1,
                {
                    ON_BATTLE_END: self.tick_status
                },
                {
                    ATTACK: 0,
                    DEFENSE: 0,
                    MAGIC: 0,
                },
                {DEBUFF, CLEANSABLE}
            ),
            "burn": lambda duration = 5: Status(
                "burn",
                "Burn",
                duration,
                {
                    ON_TURN_END: self.burn_tick,
                    ON_0_DURATION: lambda ctx, status: self.log(f"{ctx.user.pronouns['possessive']} burn faded."),
                },
                {
                    "display_text": "Burn"
                },
                {DEBUFF, CLEANSABLE}

            ),
            "poison": lambda duration = 5: Status(
                "poison",
                "Poison",
                duration,
                {
                    ON_TURN_START: self.poison_tick,
                    ON_0_DURATION: lambda ctx, status: self.log(f"{ctx.user.pronouns['possessive']} poison faded."),
                },
                {
                    "display_text": "Poison"
                },
                {DEBUFF, CLEANSABLE}

            ),
            "rage": lambda duration = 3: Status(
                "rage",
                "Rage",
                duration,
                {
                    ON_TURN_START: self.tick_status,
                    ON_PRE_DAMAGE: self.rage_pre_damage,
                    ON_0_DURATION: lambda ctx, status: self.log(f"{ctx.user.name} calmed down!")
                },
                {
                    "display_text": "Rage"
                },
                {BUFF}
            ),
            "sheep": lambda duration = 0: Status(
                "sheep",
                "Sheep",
                duration or random.randint(1, 2),
                {
                    ON_PRE_DAMAGE: self.sheep_pre_damage,
                    ON_0_DURATION: lambda ctx, status: self.log("    The sheep disappeared.")
                },
                {
                    "display_text": "Sheep",
                    "first_sheep": True
                },
                {BUFF}
            ),
            "sheepda": lambda duration = 3: Status(
                "sheepda",
                "Sheepda",
                duration,
                {
                    ON_TURN_START: self.tick_status,
                    ON_PRE_DAMAGE: self.sheep_pre_damage,
                    ON_0_DURATION: lambda ctx, status: self.log(f"{ctx.user.pronouns['possessive']} sheep disappeared.")
                },
                {
                    "display_text": "Sheepda",
                    "first_sheep": True
                },
                {BUFF}
            ),
            "sleep": lambda duration = 3: Status(
                "sleep",
                "Sleep",
                duration,
                {
                    ON_TURN_START: self.sleep_turn_start,
                    ON_POST_DAMAGE: self.sleep_post_damage,
                    ON_0_DURATION: lambda ctx, status: self.log(f"    {ctx.user.name} woke up!")
                },
                {
                    "display_text": "Asleep",
                },
                {DEBUFF, CLEANSABLE}
            ),
            "speedy_mp_recovery": lambda duration = -1: Status(
                "speedy_mp_recovery",
                "Speedy MP Recovery",
                duration,
                {
                    ON_TURN_START: self.speedy_regen_mp_tick
                },
                {
                    "mp_gain": 1
                },
                {BUFF, "permanent"}
            ),
            "valor": lambda duration = 3: Status(
                "valor",
                "Valor",
                duration,
                {
                    ON_TURN_START: self.tick_status,
                    ON_0_DURATION: lambda ctx, status: self.log(f"{ctx.user.name}'s Valor wore off.")
                },
                {
                    "display_text": "Valor",
                    ATTACK: 10,
                    DEFENSE: 10
                },
                {BUFF}
            ),
        }

        self.text_formatter = {
            "attack": {"verb": "used"},
            "item": {"verb": "used", "article": lambda name: "an " if name[0] in "aeiou" else "a "},
            "spell": {"verb": "cast"},
            "special": {"verb": "activated"}
        }

        self.battle_prep()

    def battle_prep(self, e = None, allow_forfeit = False):
        self.turn = PLAYER
        self.action = None
        self.selected_move = None
        self.menu = MENU_MAIN
        self.menu_stack = []
        self.select_enemy(e)
        self.running = True
        self.buttons = []
        self.ran_away = False
        self.battle_over = False
        if hasattr(self.player, "special_used"):
            self.player.special_used = False
        if hasattr(self.player, "get_status") and self.player.get_status("sheep") != None:
            self.player.get_status("sheep").data["first_sheep"] = True
        self.combat_log = []
        self.log_offset = 0  # for scrolling
        self.max_log_lines = 6
        self.allow_forfeit = allow_forfeit

    def log(self, message):
        if message == None:
            return
        
        self.combat_log.append(message)
        # print(message)

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

    def make_character_select_buttons(self, characters):
        self.buttons.clear()
        for i, character in enumerate(characters):
            self.buttons.append(Button((300, 150 + i * 60, 200, 40), character[NAME], lambda c=character: self.select_character(c)))

    def read_character_file(self):
        with open(getCurrentDirectory() + "characters.csv", 'r') as f:
            characters = []
            lines = f.readlines()
            header = lines[0]
            keys = header.split(";")
            for line in lines:
                if line == lines[0]:
                    continue
                data = {}
                values = line.split(";")
                for i in range(len(keys)):
                    key = keys[i].strip()
                    value = values[i].strip()
                    if key in ["moves", "inventory", "spells"]:
                        data[key] = value.split(',') if value.strip() != "" else []
                        for i in range(len(data[key])):
                            data[key][i] = data[key][i].strip()
                    elif key in [HP, MAX_HP, ATTACK, DEFENSE, MAGIC, MP, MAX_MP]:
                        data[key] = int(value.strip())
                    else:
                        data[key] = value.strip()
                characters.append(data)
            return characters

    def select_character(self, character):
        self.player = Player(**character)
        self.in_character_select = False
        self.running = False

    def run_character_select(self):
        """
        Runs ONLY the character select screen.
        Blocks execution until a character is chosen.
        """
        self.in_character_select = True
        self.running = True
        characters = self.read_character_file()
        self.make_character_select_buttons(characters)

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
        if self.turn != PLAYER:
            return
        y_offset = 400
        spacing = 40
        if self.menu == MENU_MAIN:
            options = []
            if self.player.hp <= self.player.max_hp / 2 and not self.player.special_used:
                options.append(("Special", lambda: self.set_menu(MENU_SPECIAL), None))
            options.append(("Attack", lambda: self.set_menu(MENU_ATTACK), None))
            options.append(("Items", lambda: self.set_menu(MENU_ITEMS), None))
            options.append(("Spells", lambda: self.set_menu(MENU_SPELLS), None))
            if self.allow_forfeit:
                options.append(("Forfeit", self.forfeit_battle, None))
            else:
                options.append(("Run", self.try_escape, None))

        elif self.menu == MENU_ATTACK:
            options = []
            for move_id in self.player.moves:
                move = self.get_ability(move_id)
                hover = move.get(HOVER, "")
                if DAMAGE in move:
                    base_damage = move[DAMAGE](ctx)
                    min_damage = max(0, base_damage - 3)
                    max_damage = max(0, base_damage + 3)
                    hover += f"Damage: {min_damage}-{max_damage} "
                if HITS in move:
                    hover += f"(x{move['hits']}) "
                if FUNC in move:
                    # hover += "status move"
                    pass
                options.append((move[NAME], lambda m=move_id: self.select_move(ctx, m), hover))
            options.append(("Back", self.go_back, None))
            
        elif self.menu == MENU_SPELLS:
            options = []
            for spell_id in self.player.spells:
                spell = self.get_ability(spell_id)
                spell_mp = spell.get(COST, {}).get(MP, 0)
                hover = spell.get(HOVER)
                if DAMAGE in spell:
                    base_damage = spell["damage"](ctx)
                    min_damage = max(1, base_damage - 3)
                    max_damage = max(1, base_damage + 3)
                    hover = f"Damage: {min_damage}-{max_damage}"
                if self.player.mp >= spell_mp:
                    options.append((f"{spell[NAME]} ({spell_mp} MP)", lambda s=spell_id: self.cast_spell(ctx, s), hover))
            options.append(("Back", self.go_back, None))
            
        elif self.menu == MENU_ITEMS:
            options = []
            items = list(set(self.player.inventory))
            for item_id in items:
                item = self.get_ability(item_id)
                options.append((f"{item[NAME]} x{self.player.inventory.count(item_id)}", lambda i=item_id: self.use_item(ctx, i), item.get(HOVER)))
            options.append(("Back", self.go_back, None))

        elif self.menu == MENU_SPECIAL:
            special = self.get_ability(self.player.special)
            options = [
                (special[NAME], self.set_special, special.get(HOVER, None)),
                ("Back", self.go_back, None)
            ]

        elif self.menu == MENU_QUIT:
            options = [("Quit", self.quit_game, None)]
        
        else:
            return

        for i, (text, callback, hover) in enumerate(options):
            width = max(200, font.size(text)[0] + 20)
            self.buttons.append(Button((50, y_offset + i * spacing, width, 30), text, callback, hover))

    def set_menu(self, menu):
        if self.menu != MENU_QUIT:
            self.menu = menu
        self.make_buttons()

    def go_back(self):
        self.set_menu(MENU_MAIN)

    def set_special(self):
        self.player.special_used = True
        self.action = ACTION_SPECIAL
        self.selected_move = self.player.special
        self.set_menu(MENU_MAIN)

    def forfeit_battle(self):
        self.log("You forfeited the battle.")
        self.ran_away = True
        self.end_battle()

    def try_escape(self, chance = 25):
        chance = max(chance, (1 - self.enemy.hp / self.enemy.max_hp) * 100)
        if random.randint(1, 100) <= chance:
            self.log("You escaped!")
            self.ran_away = True
            self.end_battle()
        else:
            self.log("You failed to escape!")
            self.turn = ENEMY
        self.make_buttons()

    def select_move(self, ctx, move):
        self.selected_move = move
        self.action = ACTION_ATTACK
        self.make_buttons()

    def use_item(self, ctx, item_name):
        if item_name not in ctx.user.inventory:
            print("Item not in inventory:", item_name)
            return
        self.selected_move = item_name
        self.action = ACTION_ITEM
        self.make_buttons()

    def cast_spell(self, ctx, spell_id):
        spell = self.get_ability(spell_id)
        if self.player.mp >= spell.get(COST, {}).get(MP, 0):
            self.selected_move = spell_id
            self.action = ACTION_SPELL
        else:
            self.log("Not enough MP!")
            self.turn = ENEMY
        self.make_buttons()

    def execute_ability(self, ctx, ability, ability_id):
        self.pay_ability_costs(ctx.user, ability, ability_id)

        if DAMAGE in ability:
            ctx.ability_id = ability_id

            hits = ability.get(HITS, 1)
            if callable(hits):
                hits = hits()

            for hit in range(hits):
                if not ctx.target.is_alive():
                    break

                pre = self.apply_status_event(ctx, ctx.target, ON_PRE_DAMAGE)
                if pre["blocked_all"]:
                    break
                if pre["blocked"]:
                    continue

                damage = ability[DAMAGE](ctx)
                damage = floor(damage * pre["damage_multiplier"])
                
                message = "    "
                if hits > 1:
                    message += f"Hit {hit+1}! "
                message += f"{self.do_damage(ctx.target, damage)}"
                self.log(message)

                # Attacker post-damage
                attacker_ctx = EffectContext(self, ctx.user, ctx.target)
                self.apply_status_event(attacker_ctx, ctx.user, ON_POST_DAMAGE)

                # Defender post-damage
                defender_ctx = EffectContext(self, ctx.target, ctx.user)
                self.apply_status_event(defender_ctx, ctx.target, ON_POST_DAMAGE)

        if FUNC in ability:
            result = ability[FUNC](ctx)
            if result:
                self.log(f"    {result}")

    def get_ability(self, id):
        return self.abilities[id]

    def pay_ability_costs(self, user, ability, ability_id):
        cost = ability.get(COST, {})

        # Cost
        user.mp -= cost.get(MP, 0)
        for _ in range(cost.get(COST_ITEM, 0)):
            user.inventory.remove(ability_id)

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
        if self.turn == PLAYER and self.action:
            self.player_turn()
            
        elif self.turn == ENEMY and self.enemy.is_alive():
            self.enemy_turn()
            self.end_of_round()
        
        if not self.player.is_alive() and not self.battle_over:
            self.log("You were defeated!")
            self.end_battle()

        if not self.enemy.is_alive() and not self.battle_over:
            self.log(f"You defeated the {self.enemy.name}!")
            self.end_battle()
        
        if hasattr(self, "dragon_full") and self.dragon_full and not self.battle_over:
            self.log(f"The {self.enemy.name} gets full from eating sheep and flies away!")
            self.end_battle()

    def end_battle(self):
        self.battle_over = True
        self.end_of_battle()
        self.turn = PLAYER
        self.set_menu(MENU_QUIT)

    def quit_game(self):
        self.running = False

    def change_turn(self, p):
        next_user = self.enemy if p == ENEMY else self.player
        next_target = self.player if p == ENEMY else self.enemy

        new_ctx = EffectContext(self, next_user, next_target)

        can_act = self.start_of_turn(new_ctx)

        if not can_act:
            # immediately pass turn
            self.end_of_turn(new_ctx)
            next_p = PLAYER if p == ENEMY else ENEMY
            self.change_turn(next_p)
            return

        # Set turn
        self.turn = p

        # Set menu based on turn
        if self.turn == PLAYER:
            self.set_menu(MENU_MAIN)
        else:
            self.set_menu(MENU_NONE)

    def player_turn(self):
        ctx = EffectContext(self, self.player, self.enemy)

        ability = self.get_ability(self.selected_move)
        verb = self.text_formatter[self.action]["verb"]
        article = self.text_formatter[self.action].get("article", "")
        if article != "":
            article = article(ability[NAME])

        self.log(f"{ctx.user.pronouns['subject']} {verb} {article}{ability[NAME]}!")
        self.execute_ability(ctx, ability, self.selected_move)
        if self.battle_over:
            self.action = ""
            self.selected_move = ""
            return

        if self.action == ACTION_SPECIAL:
            self.action = ""
            self.selected_move = ""
            self.set_menu(MENU_MAIN)
            return
        
        self.action = ""
        self.selected_move = ""
        self.end_of_turn(ctx)

    def enemy_turn(self):
        ctx = EffectContext(self, self.enemy, self.player)

        if getattr(self, "skip_turn", None):
            self.skip_turn = False
            self.end_of_turn(self.enemy)
            return

        if self.enemy.hp <=self.enemy.max_hp / 2 and getattr(self.enemy, ACTION_SPECIAL, None):
            ability_id = self.enemy.special
            ability = self.get_ability(ability_id)
            verb = self.text_formatter[ACTION_SPECIAL]["verb"]
            self.log(f"{self.enemy.name} {verb} {ability[NAME]}!")
            self.execute_ability(ctx, ability, ability_id)
            self.enemy.special = None

        # heal if low on hp and healing available.
        missing_hp = self.enemy.max_hp - self.enemy.hp
        usable_heals = []

        for ability_type, ability_id in self.get_enemy_abilities(self.enemy):
            ability = self.get_ability(ability_id)

            if HEAL not in ability:
                continue

            cost = ability.get(COST, {})

            if MP in cost and self.enemy.mp < cost[MP]:
                continue
            if COST_ITEM in cost and self.enemy.inventory.count(ability_id) < cost[COST_ITEM]:
                continue

            heal_value = ability.get(HEAL, 0)

            if missing_hp >= heal_value:
                usable_heals.append((ability_type, ability_id, ability))

        if usable_heals and self.enemy.hp <= 20:
            ability_type, ability_id, ability = random.choice(usable_heals)

            verb = self.text_formatter[ability_type]["verb"]
            self.log(f"{self.enemy.name} {verb} {ability[NAME]}!")

            self.execute_ability(ctx, ability, ability_id)
        else:
            abilities = self.get_usable_enemy_abilities(self.enemy)

            if not abilities:
                self.log("The enemy hesitates...")
            else:
                ability_type, ability_id = random.choice(abilities)
                ability = self.get_ability(ability_id)

                verb = self.text_formatter[ability_type]["verb"] 
                self.log(f"{self.enemy.name} {verb} {ability[NAME]}!")
                self.execute_ability(ctx, ability, ability_id)

        self.end_of_turn(ctx)
                
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

        for ability_type, id in abilities:
            ability = self.get_ability(id)

            cost = ability.get(COST, {})
            if MP in cost and enemy.mp < cost[MP]:
                continue
            if COST_ITEM in cost and enemy.inventory.count(id) < cost[COST_ITEM]:
                continue

            # healing filter
            if HEAL in ability:
                missing_hp = enemy.max_hp - enemy.hp
                if missing_hp <= ability.get(HEAL, 0): 
                    continue

            usable.append((ability_type, id))
            
        return usable

    def start_of_turn(self, ctx):
        # print("Start of turn")
        start = self.apply_status_event(ctx, ctx.user, ON_TURN_START)
        self.handle_regen_mp(ctx.user)
        return not start["skip_turn"]

    def end_of_turn(self, ctx):
        self.apply_status_event(ctx, ctx.user, ON_TURN_END)
        self.cleanup_statuses(ctx.user)
        if ctx.user == self.player:
            self.change_turn(ENEMY)
        else:
            self.change_turn(PLAYER)

    def end_of_round(self):
        pygame.display.flip()
        pygame.time.delay(1000)

    def end_of_battle(self):
        ctx = EffectContext(self, self.player, self.enemy)
        self.apply_status_event(ctx, self.player, ON_BATTLE_END)
        self.apply_status_event(ctx, self.enemy, ON_BATTLE_END)
        self.cleanup_statuses(self.player)
        self.cleanup_statuses(self.enemy)

    def add_status(self, entity, status, replace_duration = True):
        existing = entity.get_status(status.id)

        if existing:
            if replace_duration:
                existing.duration = status.duration
            else:
                existing.duration += status.duration

        else:
            entity.statuses.append(status)
            if ON_APPLY in status.handlers:
                status.handlers[ON_APPLY](EffectContext(self, entity, None), status)

    def apply_status_event(self, ctx, entity, event):
        result = {
            "blocked_all": False,   # stop all attacks/hits
            "blocked": False,       # stop one attack/hit
            "skip_turn": False,
            "end_battle": False,
            "damage_multiplier": 1.0
        }

        for status in list(entity.statuses):
            if status.duration == 0:
                continue

            handler = status.handlers.get(event)
            if not handler:
                continue

            r = handler(ctx, status)
            if not r:
                continue

            # Merge booleans (OR logic)
            if r.get("blocked_all"):
                result["blocked_all"] = True
            if r.get("blocked"):
                result["blocked"] = True
            if r.get("skip_turn"):
                result["skip_turn"] = True
            if r.get("end_battle"):
                result["end_battle"] = True

            # Combine modifiers
            if "damage_multiplier" in r:
                result["damage_multiplier"] *= r["damage_multiplier"]

            # Early exit for hard stops
            if result["blocked"] or result["skip_turn"] or result["end_battle"]:
                break

        return result
    
    def cleanup_statuses(self, entity):
        entity.statuses = [s for s in entity.statuses if s.duration > 0]

    def tick_status(self, ctx, status):
        status.reduce_duration(ctx, 1)

    def handle_regen_mp(self, entity): 
        entity.restore_mp(1)

    def do_damage(self, target, val):
        damage = max(1, damage_variance(val))
        return target.take_damage(damage)

    def kill_dragon(self, ctx):
        if getattr(ctx.target, "species", None) == "Dragon":
            ctx.target.hp = 0
            return "The Dragon falls dead."
        else:
            return "But it had no effect."
    
    def summon_sheep(self, user, attacks = 0):
        status = self.status_defs["sheep"]()
        if attacks != 0:
            status.duration = attacks
        user.statuses.append(status)
        return "A sheep blocks the next attack!"

    def sheep_pre_damage(self, ctx, status):
        attacker = ctx.user
        
        if getattr(attacker, "species", None) == "Dragon" and ctx.ability_id == "bite":
            self.log(f"    {attacker.name} takes a bite of sheep.")
            attacker.sheep_eaten = getattr(attacker, "sheep_eaten", 0) + 1
            if attacker.sheep_eaten >= 10:
                self.dragon_full = True
        else:
            result = f"    But, a sheep blocked the attack"
            if status.data["first_sheep"]:
                status.data["first_sheep"] = False
            else:
                result += " again"
            result += "."
            self.log(result)

        if status.id != "sheepda":
            status.reduce_duration(ctx, 1)
        return {"blocked": True}
    
    def valor(self, user):
        self.add_status(user, self.status_defs["valor"]())
    
    def valor_apply(self, ctx, status):
        self.log(f"    {ctx.user.name}'s Attack and Defense increased!")

    def valor_end(self, ctx, status):
        self.log(f"{ctx.user.name}'s Valor wore off.")

    def rage(self, user):
        self.add_status(user, self.status_defs["rage"]())
        self.log(f"    {user.name} now takes half damage from attacks.")
    
    def rage_pre_damage(self, ctx, status):
        return {"damage_multiplier": .5}

    def sheepda(self, user):
        self.add_status(user, self.status_defs["sheepda"]())
        return "You summon a flock of sheep that goes away in 3 turns."
    
    def armor_up(self, user):
        user.hp += user.max_hp
        return "You fortify your armor."
    
    def sleep(self, target, turns = 0):
        template = self.status_defs["sleep"]()
        status = target.get_status("sleep")
        if status != None:
            status.duration = template.duration
        else:
            status = template
            if turns != 0:
                status.duration = turns
            target.statuses.append(status)
        return f"{target.name} has fallen asleep."

    def sleep_turn_start(self, ctx, status):
        self.log(f"{ctx.user.name} is asleep!")

        status.reduce_duration(ctx, 1)

        return {"skip_turn": True}

    def sleep_post_damage(self, ctx, status):
        status.reduce_duration(ctx, status.duration)
    
    def speedy_regen_mp(self, entity):
        self.add_status(entity, self.status_defs["speedy_mp_recovery"]())

    def speedy_regen_mp_tick(self, ctx, status):
        ctx.user.restore_mp(status.data["mp_gain"])

    def poison(self, entity, val = 5):
        self.add_status(entity, self.status_defs["poison"](val), False)

    def poison_tick(self, ctx, status):
        self.log(f"{ctx.user.name} took {status.duration} Poison damage.")
        ctx.user.take_damage(status.duration)
        self.tick_status(ctx, status)

    def burn(self, entity, val = 5):
        self.add_status(entity, self.status_defs["burn"](val), False)

    def burn_tick(self, ctx, status):
        self.log(f"{ctx.user.name} took {status.duration} Burn damage.")
        ctx.user.take_damage(status.duration)
        self.tick_status(ctx, status)

    def increase_stat(self, entity, stat, val):
        status = self.status_defs["stats_up"]()
        status.data[stat] = val
        entity.statuses.append(status)
        return f"{entity.pronouns['possessive']} {stat} increased by {val}."

    def decrease_stat(self, entity, stat, val):
        status = self.status_defs["stats_down"]()
        status.data[stat] = val
        entity.statuses.append(status)
        return f"{entity.pronouns['possessive']} {stat} decreased by {val}."


if __name__ == "__main__":
    game = BattleGame()
    game.run_character_select()
    game.battle_prep("Goblin")
    # game.enemy.special = "lambda"
    game.make_buttons()
    game.run_battle()
    game.battle_prep("Goblin")
    game.make_buttons()
    game.run_battle()
    pygame.quit()
    sys.exit()