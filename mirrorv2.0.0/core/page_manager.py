import time

class PageManager:
    def __init__(self, pages):
        self.pages = pages
        self.index = 0
        self.started_at = time.time()

    def update(self):
        now = time.time()
        current = self.pages[self.index]

        if now - self.started_at >= current.duration:
            self.index = (self.index + 1) % len(self.pages)
            self.started_at = now

    def current_page(self):
        return self.pages[self.index]