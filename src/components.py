import pygame


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (255, 255, 255)
        self.text = text

    def draw(self, screen: pygame.surface.Surface, font: pygame.font.Font) -> None:
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, (0, 0, 0))
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
