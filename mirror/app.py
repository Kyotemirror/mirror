import pygame
import sys
import json

from state import MirrorState

# ============================================================
# Screen configuration (3.5" GPIO LCD)
# ============================================================
WIDTH, HEIGHT = 480, 320
FPS = 30


# ============================================================
# Load configuration from config.json
# ============================================================
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


class MirrorApp:
    def __init__(self):
        # ----------------------------------------------------
        # Initialize pygame
        # ----------------------------------------------------
        pygame.init()
        pygame.font.init()

        # ----------------------------------------------------
        # Create display (fullscreen, no window frame)
        # ----------------------------------------------------
        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.FULLSCREEN | pygame.NOFRAME
        )
        pygame.display.set_caption("Smart Mirror")

        # Hide mouse cursor (mirror-style UI)
        pygame.mouse.set_visible(False)

        # ----------------------------------------------------
        # Timing
        # ----------------------------------------------------
        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # Load config + app state
        # ----------------------------------------------------
        config = load_config()
        self.state = MirrorState(config)

        self.running = True

    # ========================================================
    # Main loop
    # ========================================================
    def run(self):
        print("✅ Mirror app started")

        try:
            while self.running:
                self.handle_events()
                self.state.update()
                self.state.draw(self.screen)

                pygame.display.flip()
                self.clock.tick(FPS)

        except KeyboardInterrupt:
            # Allows clean exit via Ctrl+C over SSH
            print("⌨️  Keyboard interrupt received")

        finally:
            self.shutdown()

    # ========================================================
    # Event handling
    # ========================================================
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Development exit keys
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

            # Forward events to state if supported
            if hasattr(self.state, "handle_event"):
                self.state.handle_event(event)

    # ========================================================
    # Cleanup
    # ========================================================
    def shutdown(self):
        print("🛑 Mirror app stopped")
        pygame.quit()
        sys.exit(0)


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    app = MirrorApp()
    app.run()
