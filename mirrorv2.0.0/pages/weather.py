import json
import time
import requests
import pygame
from datetime import datetime

from paths import path


# =========================
# Config + Cache
# =========================
CONFIG_PATH = path("config.json")
CACHE_PATH = path("data", "cache", "weather.json")

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

WEATHER_CFG = CONFIG.get("weather", {})

LAT = WEATHER_CFG.get("latitude", 0)
LON = WEATHER_CFG.get("longitude", 0)
UNITS = WEATHER_CFG.get("units", "imperial")
CACHE_SECONDS = WEATHER_CFG.get("cache_seconds", 900)

TEMP_UNIT = "°F" if UNITS == "imperial" else "°C"
WIND_UNIT = "mph" if UNITS == "imperial" else "km/h"


# =========================
# Data Fetching
# =========================
def fetch_weather():
    # Use cache if still valid
    if CACHE_PATH.exists():
        age = time.time() - CACHE_PATH.stat().st_mtime
        if age < CACHE_SECONDS:
            with open(CACHE_PATH, "r") as f:
                return json.load(f)

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}"
        f"&longitude={LON}"
        "&current_weather=true"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&timezone=auto"
        f"&temperature_unit={'fahrenheit' if UNITS == 'imperial' else 'celsius'}"
        f"&windspeed_unit={'mph' if UNITS == 'imperial' else 'kmh'}"
    )

    r = requests.get(url, timeout=5)
    r.raise_for_status()
    data = r.json()

    with open(CACHE_PATH, "w") as f:
        json.dump(data, f)

    return data


# =========================
# Rendering
# =========================
def render(screen, fonts):
    screen.fill((0, 0, 0))

    try:
        data = fetch_weather()
    except Exception:
        text = fonts["body"].render("Weather unavailable", True, (180, 180, 180))
        screen.blit(text, (60, 140))
        return

    current = data.get("current_weather", {})
    daily = data.get("daily", {})

    # --- Current ---
    temp = current.get("temperature")
    wind = current.get("windspeed")

    title = fonts["title"].render("Weather", True, (220, 220, 220))
    screen.blit(title, (60, 40))

    if temp is not None:
        temp_text = fonts["clock"].render(f"{int(temp)}{TEMP_UNIT}", True, (255, 255, 255))
        screen.blit(temp_text, (60, 110))

    if wind is not None:
        wind_text = fonts["body"].render(f"Wind: {int(wind)} {WIND_UNIT}", True, (180, 180, 180))
        screen.blit(wind_text, (60, 220))

    # --- Forecast ---
    times = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])

    y = 300
    for i in range(min(5, len(times))):
        day = datetime.fromisoformat(times[i]).strftime("%a")
        line = f"{day}: {int(highs[i])}{TEMP_UNIT} / {int(lows[i])}{TEMP_UNIT}"
        text = fonts["body"].render(line, True, (180, 180, 180))
        screen.blit(text, (60, y))
        y += 40
