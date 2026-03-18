import os
import sys
import json
import pygame

from state import MirrorState

# Screen configuration
WIDTH = 480
HEIGHT = 320
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

        # Fullscreen display (safe)
        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.FULLSCREEN
        )
        pygame.display.set_caption("Smart Mirror")

        pygame.mouse.set_visible(False)

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
            self.shutdown()

    def shutdown(self):
        print("🛑 Mirror app stopped")
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = MirrorApp()
    app.run()
