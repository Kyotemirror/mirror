import os

# ✅ Force SDL to use X11 on the GoodTFT LCD
os.environ["SDL_VIDEODRIVER"] = "x11"
os.environ["DISPLAY"] = ":0"

import pygame
import json
from state import MirrorState

# Load config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

# Screen config
WIDTH = CONFIG["screen"]["width"]
HEIGHT = CONFIG["screen"]["height"]
FPS = CONFIG["screen"]["fps"]


class MirrorApp:
    def __init__(self):
        pygame.init()

        # ✅ Hide mouse cursor (mirror polish)
        pygame.mouse.set_visible(False)

        # ✅ Create display on LCD
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Smart Mirror")

        self.clock = pygame.time.Clock()
        self.state = MirrorState(CONFIG)
        self.running = True

    def run(self):
        print("✅ Mirror app started")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.state.update()
            self.state.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        print("🛑 Mirror app stopped")


if __name__ == "__main__":
    app = MirrorApp()
    app.run()

class MirrorApp:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Smart Mirror")

        self.clock = pygame.time.Clock()
        self.state = MirrorState(CONFIG)
        self.running = True

    def run(self):
        print("✅ Mirror app started")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.state.update()
            self.state.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        print("🛑 Mirror app stopped")


if __name__ == "__main__":
    app = MirrorApp()
    app.run()
