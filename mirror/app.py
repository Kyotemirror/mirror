import pygame
import sys
import json
import os

from state import MirrorState

# ============================================================
# Screen configuration (3.5" GPIO LCD)
# ============================================================
WIDTH, HEIGHT = 480, 320
FPS = 30


# ============================================================
# Load configuration (always relative to this file)
# ============================================================
def load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")

    with open(config_path, "r") as f:
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

        # Hide mouse cursor (mirror UI)
        pygame.mouse.set_visible(False)

        # ----------------------------------------------------
        # Timing
        # ----------------------------------------------------
        self.clock = pygame.time.Clock()

        # ----------------------------------------------------
        # Load config + initialize state
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
                # Dev exit keys
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

            # Forward events to state if implemented
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
