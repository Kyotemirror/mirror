import pygame
from datetime import datetime


class MirrorState:
    def __init__(self):
        # Font setup
        # None = default font (safe on Raspberry Pi)
        self.font = pygame.font.SysFont(None, 64)

        # Cached time string
        self.time_text = ""

    def update(self):
        # Update the clock once per frame
        self.time_text = datetime.now().strftime("%I:%M %p").lstrip("0")

    def draw(self, screen):
        # Clear screen (black background)
        screen.fill((0, 0, 0))

        # Render clock text
        text_surface = self.font.render(
            self.time_text,
            True,
            (255, 255, 255)
        )

        # Center the text on a 480x320 screen
        rect = text_surface.get_rect(center=(240, 160))
        screen.blit(text_surface, rect)
