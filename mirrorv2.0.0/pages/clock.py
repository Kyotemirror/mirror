"""
Clock page for Kyote Smart Mirror
"""

import time

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (180, 180, 180)

def render(screen, fonts):
    screen.fill(BLACK)

    time_str = time.strftime("%H:%M")
    date_str = time.strftime("%A, %B %d")

    time_text = fonts["clock"].render(time_str, True, WHITE)
    date_text = fonts["body"].render(date_str, True, GRAY)

    rect = screen.get_rect()
    screen.blit(time_text, time_text.get_rect(center=(rect.centerx, rect.centery - 20)))
    screen.blit(date_text, date_text.get_rect(center=(rect.centerx, rect.centery + 60)))