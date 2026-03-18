import requests
from datetime import datetime

class WeatherService:
    def __init__(self, latitude, longitude, units="metric"):
        self.lat = latitude
        self.lon = longitude
        self.units = units

    def fetch(self):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.lat,
            "longitude": self.lon,
            "current_weather": True
        }

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            weather = data.get("current_weather", {})
            return {
                "temperature": weather.get("temperature"),
                "windspeed": weather.get("windspeed"),
                "time": weather.get("time")
            }
        except Exception as e:
            return {
                "error": str(e),
                "time": datetime.utcnow().isoformat()
            }
