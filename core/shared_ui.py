import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Battle Game")

font = pygame.font.SysFont("arial", 24)
clock = pygame.time.Clock()


class Button:
    def __init__(self, rect, text, callback, hover_text=None, color=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.hover_text = hover_text
        self.hovered = False
        self.color = color

    def draw(self, surface):
        button_color = self.color or (50, 50, 150)

        if self.hovered:
            button_color = (100, 100, 200)

        pygame.draw.rect(surface, button_color, self.rect)

        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()
    
    def check_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

def draw_text(surface, text, x, y, color=(255, 255, 255)):
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x, y))