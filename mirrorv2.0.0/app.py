#!/usr/bin/env python3
"""
Kyote Smart Mirror - V1
Full API-enabled build with adaptive performance
Clock + Weather + Calendar + News
"""

import platform
import pygame
import time
import sys

from pages import clock as clock_page
from pages import weather, calendar, news

# =========================
# Hardware Detection
# =========================
def detect_pi_class():
    machine = platform.machine()

    # armv6 = Pi Zero / Zero W
    if machine == "armv6l":
        return "pi_zero"

    # armv7 / aarch64 = Pi 3 / 4 / 5
    return "pi_modern"


PI_CLASS = detect_pi_class()

# =========================
# Performance Presets
# =========================
if PI_CLASS == "pi_zero":
    FPS = 30
    FONT_SCALE = 0.85
    USE_FULL_RESOLUTION = False
    NEWS_SCROLL_SPEED = 12
else:
    FPS = 45
    FONT_SCALE = 1.0
    USE_FULL_RESOLUTION = True
    NEWS_SCROLL_SPEED = 20

# =========================
# Page Durations (seconds)
# =========================
CLOCK_PAGE_DURATION = 20
WEATHER_PAGE_DURATION = 20
CALENDAR_PAGE_DURATION = 20
NEWS_PAGE_DURATION = 20

# =========================
# Page System
# =========================
class Page:
    def __init__(self, name, duration, render_fn):
        self.name = name
        self.duration = duration
        self.render = render_fn


class PageManager:
    def __init__(self, pages):
        self.pages = pages
        self.index = 0
        self.started_at = time.time()

    def update(self):
        now = time.time()
        if now - self.started_at >= self.pages[self.index].duration:
            self.index = (self.index + 1) % len(self.pages)
            self.started_at = now

    def current(self):
        return self.pages[self.index]

    def page_started_at(self):
        return self.started_at

# =========================
# Fonts
# =========================
def load_fonts():
    return {
        "clock": pygame.font.SysFont("sans", int(96 * FONT_SCALE)),
        "title": pygame.font.SysFont("sans", int(48 * FONT_SCALE)),
        "body": pygame.font.SysFont("sans", int(32 * FONT_SCALE)),
    }

# =========================
# Main Application
# =========================
def main():
    pygame.init()
    pygame.font.init()

    display_info = pygame.display.Info()

    if USE_FULL_RESOLUTION:
        screen_size = (display_info.current_w, display_info.current_h)
    else:
        screen_size = (display_info.current_w // 2, display_info.current_h // 2)

    screen = pygame.display.set_mode(screen_size, pygame.FULLSCREEN)
    pygame.display.set_caption("Kyote Smart Mirror")

    pg_clock = pygame.time.Clock()
    fonts = load_fonts()

    global manager
    manager = PageManager([])

    pages = [
        Page(
            "clock",
            CLOCK_PAGE_DURATION,
            lambda s: clock_page.render(s, fonts),
        ),
        Page(
            "weather",
            WEATHER_PAGE_DURATION,
            lambda s: weather.render(s, fonts),
        ),
        Page(
            "calendar",
            CALENDAR_PAGE_DURATION,
            lambda s: calendar.render(s, fonts),
        ),
        Page(
            "news",
            NEWS_PAGE_DURATION,
            lambda s: news.render(
                s,
                fonts,
                manager.page_started_at(),
                scroll_speed=NEWS_SCROLL_SPEED,
            ),
        ),
    ]

    manager.pages = pages

    running = True
    last_draw = 0
    redraw_interval = 1 / FPS

    while running:
        pygame.event.pump()
        for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN]):
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        now = time.time()
        if now - last_draw >= redraw_interval:
            manager.update()
            manager.current().render(screen)
            pygame.display.flip()
            last_draw = now

        pg_clock.tick(FPS)

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()