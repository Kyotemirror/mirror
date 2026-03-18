import pygame
from datetime import datetime

from weather import WeatherWidget


class MirrorState:
    def __init__(self, config):
        self.config = config

        # ----------------------------------------------------
        # Clock configuration
        # ----------------------------------------------------
        clock_cfg = config.get("clock", {})
        color_cfg = config.get("colors", {})

        # Time format
        show_seconds = clock_cfg.get("show_seconds", False)
        self.time_format = "%I:%M:%S %p" if show_seconds else "%I:%M %p"

        # Font
        font_size = clock_cfg.get("font_size", 72)
        self.clock_font = pygame.font.SysFont(None, font_size)

        # Colors (JSON → tuple)
        self.text_color = tuple(color_cfg.get("text", [255, 255, 255]))
        self.bg_color = tuple(color_cfg.get("background", [0, 0, 0]))

        # Clock state
        self.time_text = ""
        self.last_time_text = None

        # ----------------------------------------------------
        # Weather widget
        # ----------------------------------------------------
        self.weather = None
        weather_cfg = config.get("weather", {})
        if weather_cfg.get("enabled", False):
            self.weather = WeatherWidget(config)

    # ----------------------------------------------------
    # Event handling (touch / keys later)
    # ----------------------------------------------------
    def handle_event(self, event):
        # Placeholder for future input handling
        pass

    # ----------------------------------------------------
    # Update logic
    # ----------------------------------------------------
    def update(self):
        now_text = datetime.now().strftime(self.time_format).lstrip("0")

        if now_text != self.last_time_text:
            self.time_text = now_text
            self.last_time_text = now_text

        if self.weather:
            self.weather.update()

    # ----------------------------------------------------
    # Rendering
    # ----------------------------------------------------
    def draw(self, screen):
        # Clear background
        screen.fill(self.bg_color)

        # -----------------------
