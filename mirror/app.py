import pygame
import sys
import json
import os

from state import MirrorState

WIDTH, HEIGHT = 480, 320
FPS = 30


def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    with open(config_path, "r") as f:
        return json.load(f)


class MirrorApp:
    def __init__(self):
        pygame.init()
        pygame.font.init()

        # ✅ WINDOWED MODE (DEBUG SAFE)
       self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Smart Mirror DEBUG")

        self.clock = pygame.time.Clock()

        config = load_config()
        self.state = MirrorState(config)

        self.running = True

    def run(self):
        print("✅ Mirror app started")

        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_ESCAPE, pygame.K_q):
                            self.running = False

                self.state.update()
                self.state.draw(self.screen)

                pygame.display.flip()
                self.clock.tick(FPS)

        finally:
            pygame.quit()
            sys.exit(0)


if __name__ == "__main__":
    MirrorApp().run()
