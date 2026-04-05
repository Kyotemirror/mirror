"""
Auto-detect device location using IP-based geolocation.
Falls back to config.json values.
Cached locally to avoid repeated lookups.
"""

import json
import os
import urllib.request

CONFIG_PATH = "/home/pi/mirror/config.json"
CACHE_FILE = "/home/pi/mirror/data/cache/location.json"

GEO_URL = "http://ip-api.com/json/"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_cache(data):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return None

def detect_location():
    # 1. Cached value
    cached = load_cache()
    if cached:
        return cached["lat"], cached["lon"], cached.get("city")

    # 2. IP-based lookup
    try:
        with urllib.request.urlopen(GEO_URL, timeout=3) as response:
            data = json.loads(response.read())
            if data.get("status") == "success":
                location = {
                    "lat": data["lat"],
                    "lon": data["lon"],
                    "city": data.get("city"),
                    "region": data.get("regionName"),
                    "country": data.get("country")
                }
                save_cache(location)
                return location["lat"], location["lon"], location["city"]
    except Exception:
        pass

    # 3. Fallback to config.json
    cfg = load_config()
    weather_cfg = cfg["weather"]
    return weather_cfg["latitude"], weather_cfg["longitude"], None