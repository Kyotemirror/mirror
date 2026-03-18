import pygame
from datetime import datetime
from weather import WeatherWidget


class MirrorState:
    def __init__(self, config):
        self.config = config

        color_cfg = config.get("colors", {})
        clock_cfg = config.get("clock", {})

        self.bg_color = tuple(color_cfg.get("background", [0, 0, 0]))
        self.text_color = tuple(color_cfg.get("text", [255, 255, 255]))

        self.clock_font = pygame.font.SysFont(
            None, clock_cfg.get("font_size", 72)
        )

        self.time_text = ""

        # ✅ Weather is optional and safe
        self.weather = WeatherWidget(config)

    def update(self):
        self.time_text = datetime.now().strftime("%I:%M %p").lstrip("0")
        self.weather.update()

    def draw(self, screen):
        screen.fill(self.bg_color)

        # Clock (centered)
        clock_surface = self.clock_font.render(
            self.time_text, True, self.text_color
        )
        clock_rect = clock_surface.get_rect(
            center=screen.get_rect().center
        )
        screen.blit(clock_surface, clock_rect)

        # Weather (top-left)
        self.weather.draw(screen)
