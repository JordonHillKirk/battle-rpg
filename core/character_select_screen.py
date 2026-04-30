from core.constants import *
from core.game_utils import getCurrentDirectory
from core.shared_ui import Button, screen, clock, font
import pygame
from core.entities import Player


class CharacterSelectScreen:
    def __init__(self):
        self.buttons = []
        self.running = False
        self.selected_player = None

    def make_character_select_buttons(self, characters):
        self.buttons.clear()
        for i, character in enumerate(characters):
            self.buttons.append(
                Button(
                    (300, 150 + i * 60, 200, 40),
                    character[NAME],
                    lambda c=character: self.select_character(c)
                )
            )

    def read_character_file(self):
        with open(getCurrentDirectory() + "characters.csv", 'r') as f:
            characters = []
            lines = f.readlines()
            keys = lines[0].split(";")

            for line in lines[1:]:
                data = {}
                values = line.split(";")

                for i in range(len(keys)):
                    key = keys[i].strip()
                    value = values[i].strip()

                    if key in ["moves", "inventory", "spells"]:
                        data[key] = value.split(',') if value else []
                        data[key] = [v.strip() for v in data[key]]

                    elif key in [HP, MAX_HP, ATTACK, DEFENSE, MAGIC, MP, MAX_MP]:
                        data[key] = int(value)

                    else:
                        data[key] = value

                characters.append(data)

        return characters

    def select_character(self, character):
        self.selected_player = Player(**character)
        self.running = False

    def run(self):
        self.running = True
        characters = self.read_character_file()
        self.make_character_select_buttons(characters)

        while self.running:
            screen.fill((0, 0, 0))

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                for button in self.buttons:
                    button.handle_event(event)

            for button in self.buttons:
                button.check_hover(mouse_pos)
                button.draw(screen)

            pygame.display.flip()
            clock.tick(60)

        pygame.display.iconify()
        return self.selected_player