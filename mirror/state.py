import pygame
from datetime import datetime
import os

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
        # Weather
        # -----------------
        self.weather = WeatherWidget(config)

        # -----------------
        # Logos
        # -----------------
        self.logo_right = None
        self.logo_left = None
        self.logo_right_rect = None
        self.logo_left_rect = None

        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        right_logo_path = os.path.join(assets_dir, "logo.png")
        left_logo_path = os.path.join(assets_dir, "logo_left.png")

        def load_logo(path):
            logo = pygame.image.load(path).convert_alpha()
            max_width = 160
            scale = max_width / logo.get_width()
            new_size = (
                int(logo.get_width() * scale),
                int(logo.get_height() * scale)
            )
            logo = pygame.transform.smoothscale(logo, new_size)
            logo.set_alpha(90)
            return logo

        try:
            if os.path.exists(right_logo_path):
                self.logo_right = load_logo(right_logo_path)
                self.logo_right_rect = self.logo_right.get_rect()
                self.logo_right_rect.bottomright = (460, 300)  # 480x320 screen

            if os.path.exists(left_logo_path) and self.logo_right_rect:
                self.logo_left = load_logo(left_logo_path)
                self.logo_left_rect = self.logo_left.get_rect()

                spacing = 10
                self.logo_left_rect.bottomright = (
                    self.logo_right_rect.left - spacing,
                    self.logo_right_rect.bottom
                )

        except Exception as e:
            print("Logo load failed:", e)

    def update(self):
        now = datetime.now()
        self.time_text = now.strftime("%I:%M %p").lstrip("0")
        self.date_text = now.strftime("%A, %b %d")
        self.weather.update()

    def draw(self, screen):
        screen.fill(self.bg_color)
        screen_rect = screen.get_rect()

        # -----------------
        # Logos
        # -----------------
        if self.logo_left and self.logo_left_rect:
            screen.blit(self.logo_left, self.logo_left_rect)

        if self.logo_right and self.logo_right_rect:
            screen.blit(self.logo_right, self.logo_right_rect)

        # -----------------
        # Date
        # -----------------
        date_surface = self.date_font.render(
            self.date_text, True, self.text_color
        )
        date_rect = date_surface.get_rect(
            center=(screen_rect.centerx, screen_rect.centery - 50)
        )
        screen.blit(date_surface, date_rect)

        # -----------------
        # Clock
        # -----------------
        clock_surface = self.clock_font.render(
            self.time_text, True, self.text_color
        )
        clock_rect = clock_surface.get_rect(
            center=screen_rect.center
        )
        screen.blit(clock_surface, clock_rect)

        # -----------------
        # Weather
        # -----------------
        self.weather.draw(screen)
