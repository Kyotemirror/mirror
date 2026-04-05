import feedparser
import time

FEED_URL = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"

def fetch_headlines():
    feed = feedparser.parse(FEED_URL)
    return [e.title for e in feed.entries[:6]]

def render(screen, fonts, page_start_time, scroll_speed=20):
    screen.fill((0,0,0))
    screen.blit(fonts["title"].render("News", True, (255,255,255)), (60,40))

    headlines = fetch_headlines()
    offset = 140 - int((time.time() - page_start) * scroll_speed)

    for i, h in enumerate(headlines):
        y = offset + i * 50
        if -40 < y < screen.get_height():
            screen.blit(fonts["body"].render("• " + h, True, (180,180,180)), (60,y))