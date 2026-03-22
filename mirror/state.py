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
        self.logo_left = None
        self.logo_right = None

        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        left_logo_path = os.path.join(assets_dir, "logo_left.png")
        right_logo_path = os.path.join(assets_dir, "logo.png")

        def load_logo(path):
            logo = pygame.image.load(path).convert_alpha()
            max_width = 160
            scale = max_width / logo.get_width()
            logo = pygame.transform.smoothscale(
                logo,
                (
                    int(logo.get_width() * scale),
                    int(logo.get_height() * scale)
                )
            )
            logo.set_alpha(180)
            return logo

        try:
            if os.path.exists(left_logo_path):
                self.logo_left = load_logo(left_logo_path)

            if os.path.exists(right_logo_path):
                self.logo_right = load_logo(right_logo_path)

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
        # Logos (CENTERED AS A GROUP)
        # -----------------
        if self.logo_left and self.logo_right:
            spacing = 10

            total_width = (
                self.logo_left.get_width()
                + spacing
                + self.logo_right.get_width()
            )
            max_height = max(
                self.logo_left.get_height(),
                self.logo_right.get_height()
            )

            group_rect = pygame.Rect(
                0, 0, total_width, max_height
            )
            group_rect.midbottom = (
                screen_rect.centerx,
                screen_rect.bottom - 10
            )

            left_rect = self.logo_left.get_rect()
            left_rect.bottomleft = group_rect.bottomleft

            right_rect = self.logo_right.get_rect()
            right_rect.bottomleft = (
                left_rect.right + spacing,
                left_rect.bottom
            )

            screen.blit(self.logo_left, left_rect)
            screen.blit(self.logo_right, right_rect)

        elif self.logo_right:
            rect = self.logo_right.get_rect()
            rect.midbottom = (
                screen_rect.centerx,
                screen_rect.bottom - 10
            )
            screen.blit(self.logo_right, rect)

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
