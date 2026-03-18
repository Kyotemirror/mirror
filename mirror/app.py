import pygame
from state import MirrorState

# Screen configuration for 3.5" GPIO LCD
WIDTH, HEIGHT = 480, 320
FPS = 30


class MirrorApp:
    def __init__(self):
        # Initialize pygame
        pygame.init()

        # Create display
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Smart Mirror")

        # Timing
        self.clock = pygame.time.Clock()

        # App state
        self.state = MirrorState()
        self.running = True

    def run(self):
        print("✅ Mirror app started")

        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Update logic
            self.state.update()

            # Draw to screen
            self.state.draw(self.screen)

            # Push frame to display
            pygame.display.flip()
            self.clock.tick(FPS)

        self.shutdown()

    def shutdown(self):
        print("🛑 Mirror app stopped")
        pygame.quit()


# -------- Entry Point --------
if __name__ == "__main__":
    app = MirrorApp()
    app.run()
