from datetime import datetime
from .weather import WeatherService

class MirrorState:
    def __init__(self, config):
        self.config = config
        loc = config.get("location")
        self.weather_service = WeatherService(
            loc["latitude"],
            loc["longitude"]
        )
        self.last_weather = None
        self.last_weather_fetch = None

    def update(self):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"🕒 {now}")

        if self.last_weather is None:
            self.last_weather = self.weather_service.fetch()
            print(f"🌤 Weather: {self.last_weather}")
