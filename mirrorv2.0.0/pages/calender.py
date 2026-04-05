from icalendar import Calendar
from datetime import datetime
import pytz

ICS_FILE = "/home/pi/mirror/data/calendar.ics"

def load_events():
    with open(ICS_FILE, "rb") as f:
        cal = Calendar.from_ical(f.read())

    events = []
    now = datetime.now(pytz.utc)

    for e in cal.walk("VEVENT"):
        start = e.decoded("dtstart")
        if start >= now:
            events.append((start, str(e.get("summary"))))

    return sorted(events)[:5]

def render(screen, fonts):
    screen.fill((0,0,0))
    screen.blit(fonts["title"].render("Calendar", True, (255,255,255)), (60,40))

    y = 120
    try:
        for start, title in load_events():
            line = f"{start.strftime('%a %H:%M')} — {title}"
            screen.blit(fonts["body"].render(line, True, (180,180,180)), (60,y))
            y += 40
    except Exception:
        screen.blit(fonts["body"].render("Calendar unavailable", True, (180,180,180)), (60,y))