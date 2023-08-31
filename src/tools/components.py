import pygame
from src.tools.utilities import clamp


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)
        self.text = text

    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font, text_color: pygame.Color) -> None:
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos: (float, float)) -> bool:
        return self.rect.collidepoint(pos)


class Label:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, background_color: pygame.Color = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.background_color = background_color

    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font, text_color: pygame.Color) -> None:
        if self.background_color is not None:
            pygame.draw.rect(screen, self.background_color, self.rect)

        text_surface = font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def set_text(self, text: str):
        self.text = text


class Dropdown:
    def __init__(self, x: int, y: int, width: int, height: int, options: list[str]):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.selected_option: str | None = None
        self.is_open = False

    def toggle_dropdown(self):
        self.is_open = not self.is_open

    def select_option(self, option: str):
        self.selected_option = option
        self.is_open = False

    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font, background_color: pygame.Color,
             text_color: pygame.Color):

        pygame.draw.rect(screen, background_color, self.rect)
        pygame.draw.rect(screen, pygame.Color("black"), self.rect, 2)

        if self.selected_option:
            selected_text = font.render(self.selected_option, True, text_color)
            screen.blit(selected_text, (self.rect.x + 10, self.rect.y + 15))

        if self.is_open:
            for i, option in enumerate(self.options):
                option_rect = pygame.Rect(self.rect.x, self.rect.y + (i + 1) * self.rect.height, self.rect.width,
                                          self.rect.height)

                pygame.draw.rect(screen, background_color, option_rect)
                pygame.draw.rect(screen, pygame.Color("black"), option_rect, 1)
                option_text = font.render(option, True, text_color)
                screen.blit(option_text, (option_rect.x + 10, option_rect.y + 15))


class Slider:
    def __init__(self, x, y, width, min_value: int, max_value: int, value: int, text="Value", step_value=1):
        self.knob_rect = None
        self.rect = pygame.Rect(x, y, width, 10)
        self.knob_radius = 10
        self.min_value = min_value
        self.max_value = max_value
        self.step_value = step_value
        self.value = value
        self.text = text

    def set_value(self, new_value):
        self.value = max(self.min_value, min(new_value, self.max_value))

    def set_text(self, new_text: str):
        self.text = new_text

    def update_value(self, mouse_x):
        percentage = (mouse_x - self.rect.left) / self.rect.width
        new_value = self.min_value + percentage * (self.max_value - self.min_value)
        new_value = round(new_value / self.step_value) * self.step_value
        self.set_value(new_value)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, color: pygame.Color):
        pygame.draw.rect(screen, color, self.rect)

        knob_x = (self.rect.left + (self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        knob_center = (knob_x, self.rect.centery)
        self.knob_rect = pygame.draw.circle(screen, pygame.Color('black'), knob_center, self.knob_radius)

        text_surface = font.render(f"{self.text}: {self.value}", True, pygame.Color('black'))
        text_rect = text_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)


class RGBPicker:
    def __init__(self, x, y, width, height, color: (int, int, int), min_value=0, max_value=255, display_preview=False):
        if display_preview:
            self.rect = pygame.Rect(x, y, width + 130, height + 21)
        else:
            self.rect = pygame.Rect(x, y, width + 50, height + 21)
        self.color = color
        self.sliders = [
            Slider(x + 5, y + 10, 200, min_value, max_value, color[0], "R"),
            Slider(x + 5, y + 30, 200, min_value, max_value, color[1], "G"),
            Slider(x + 5, y + 50, 200, min_value, max_value, color[2], "B")
        ]
        self.display_preview = display_preview

    def update_color(self):
        self.color = (int(self.sliders[0].value), int(self.sliders[1].value), int(self.sliders[2].value))

    def draw(self, screen, font, background_color: pygame.Color, slider_background_color: pygame.Color):
        pygame.draw.rect(screen, background_color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)

        for slider in self.sliders:
            slider.draw(screen, font, slider_background_color)

        if self.display_preview:
            color_preview_rect = pygame.Rect(self.rect.right - 70, self.rect.topright[1], 70, 70)
            new_color = (clamp(int(self.color[0]), 0, 0, 255),
                         clamp(int(self.color[1]), 0, 0, 255),
                         clamp(int(self.color[2]), 0, 0, 255))
            pygame.draw.rect(screen, pygame.Color(new_color), color_preview_rect)
            pygame.draw.rect(screen, (0, 0, 0), color_preview_rect, 2)
