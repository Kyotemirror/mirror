import time
from .state import MirrorState
from .config import Config

class MirrorApp:
    def __init__(self, config_path="config.json"):
        self.config = Config(config_path)
        self.state = MirrorState(self.config)
        self.running = True

    def run_forever(self):
        print("✅ Mirror service started")
        try:
            while self.running:
                self.state.update()
                time.sleep(1)
        except KeyboardInterrupt:
            self.shutdown()

    def run_once(self):
        self.state.update()

    def shutdown(self):
        print("🛑 Mirror service stopped")
        self.running = False
