import pygame
from datetime import datetime

from weather import WeatherWidget



class MirrorState:
    def __init__(self, config):
        self.config = config

        # -----------------
        # Colors
        # -----------------
        color_cfg = config.get("colors", {})
        self.bg_color = tuple(color_cfg.get("background", [0, 0, 0]))
        self.text_color = tuple(color_cfg.get("text", [255, 255, 255]))

        # -----------------
        # Clock / Date
        # -----------------
        clock_cfg = config.get("clock", {})
        self.clock_font = pygame.font.SysFont(
            None, clock_cfg.get("font_size", 72)
        )
        self.date_font = pygame.font.SysFont(None, 32)

        self.time_text = ""
        self.date_text = ""

        # -----------------
        # Widgets
        # -----------------
        self.weather = WeatherWidget(config)
        
    def update(self):
        now = datetime.now()

        self.time_text = now.strftime("%I:%M %p").lstrip("0")
        self.date_text = now.strftime("%A, %b %d")

        self.weather.update()
        

    def draw(self, screen):
        screen.fill(self.bg_color)

        screen_rect = screen.get_rect()

        # -----------------
        # Date (above clock)
        # -----------------
        date_surface = self.date_font.render(
            self.date_text, True, self.text_color
        )
        date_rect = date_surface.get_rect(
            center=(screen_rect.centerx, screen_rect.centery - 50)
        )
        screen.blit(date_surface, date_rect)

        # -----------------
        # Clock (center)
        # -----------------
        clock_surface = self.clock_font.render(
            self.time_text, True, self.text_color
        )
        clock_rect = clock_surface.get_rect(center=screen_rect.center)
        screen.blit(clock_surface, clock_rect)

        # -----------------
        # Weather (top-left)
        # -----------------
        self.weather.draw(screen)
        
