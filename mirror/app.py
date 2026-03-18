import pygame
from .state import MirrorState

WIDTH, HEIGHT = 480, 320
FPS = 30


class MirrorApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Smart Mirror")

        self.clock = pygame.time.Clock()
        self.state = MirrorState()
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
