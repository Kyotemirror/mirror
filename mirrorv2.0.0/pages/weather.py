"""
Weather page for Kyote Smart Mirror
Provider: Open‑Meteo
Includes: Current weather + 7‑day forecast
Supports Metric (°C) and Imperial (°F)
"""

import json
import os
import time
import urllib.request
from datetime import datetime
from location import detect_location
# -------------------------
# Load config
# -------------------------
CONFIG_PATH = "/home/pi/mirror/config.json"

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

WEATHER_CFG = CONFIG["weather"]
CACHE_DIR = CONFIG["paths"]["cache"]
CACHE_FILE = os.path.join(CACHE_DIR, "weather.json")

LAT = WEATHER_CFG["latitude"]
LON = WEATHER_CFG["longitude"]
UNITS = WEATHER_CFG.get("units", "metric")
CACHE_SECONDS = WEATHER_CFG["cache_seconds"]

# -------------------------
# Helpers
# -------------------------
def c_to_f(c):
    return round((c * 9 / 5) + 32)

def fmt_temp(c):
    if UNITS == "imperial":
        return f"{c_to_f(c)}°F"
    return f"{int(c)}°C"

# -------------------------
# Open‑Meteo endpoint
# -------------------------
API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}"
    f"&longitude={LON}"
    "&current_weather=true"
    "&daily=temperature_2m_max,temperature_2m_min,weathercode"
    "&forecast_days=7"
    "&timezone=auto"
)

# -------------------------
# Fetch + cache weather
# -------------------------
def fetch_weather():
    if os.path.exists(CACHE_FILE):
        age = time.time() - os.path.getmtime(CACHE_FILE)
        if age < CACHE_SECONDS:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)

    try:
        with urllib.request.urlopen(API_URL, timeout=3) as response:
            data = json.loads(response.read())
            os.makedirs(CACHE_DIR, exist_ok=True)
            with open(CACHE_FILE, "w") as f:
                json.dump(data, f)
            return data
    except Exception:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        return None

# -------------------------
# Render page
# -------------------------
def render(screen, fonts):
    screen.fill((0, 0, 0))

    screen.blit(
        fonts["title"].render("Weather", True, (255, 255, 255)),
        (60, 40),
    )

    data = fetch_weather()
    if not data:
        screen.blit(
            fonts["body"].render("Weather unavailable", True, (180, 180, 180)),
            (60, 120),
        )
        return

    # -------------------------
    # Current weather
    # -------------------------
    current = data.get("current_weather", {})
    temp = current.get("temperature")
    wind = current.get("windspeed")

    screen.blit(
        fonts["body"].render(f"Now: {fmt_temp(temp)}", True, (180, 180, 180)),
        (60, 120),
    )
    screen.blit(
        fonts["body"].render(f"Wind: {int(wind)} km/h", True, (180, 180, 180)),
        (60, 155),
    )

    # -------------------------
    # Weekly forecast
    # -------------------------
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    t_max = daily.get("temperature_2m_max", [])
    t_min = daily.get("temperature_2m_min", [])

    y = 220
    for i in range(min(7, len(dates))):
        day = datetime.fromisoformat(dates[i]).strftime("%a")
        line = f"{day}: {fmt_temp(t_min[i])} / {fmt_temp(t_max[i])}"

        screen.blit(
            fonts["body"].render(line, True, (160, 160, 160)),
            (60, y),
        )
        y += 35