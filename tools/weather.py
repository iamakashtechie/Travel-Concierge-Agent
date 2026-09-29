from dataclasses import dataclass
import json
import os
import time
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class WeatherProvider(Protocol):
  def fetch(self, destination: str, timeout_seconds: float) -> dict:
    ...


class DemoWeatherProvider:
  _forecasts = {
    "amsterdam": {
      "forecast": "Cool and partly cloudy",
      "temperature_c": 14,
    },
    "tokyo": {
      "forecast": "Mild with light rain possible",
      "temperature_c": 19,
    },
  }

  def fetch(self, destination: str, timeout_seconds: float) -> dict:
    del timeout_seconds
    forecast = self._forecasts.get(destination.lower())
    if forecast is None:
      return {
        "status": "error",
        "message": f"No weather data is available for {destination}.",
      }
    return {
      "status": "success",
      "source": "demo_weather_provider",
      **forecast,
    }


class OpenMeteoWeatherProvider:
  geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
  forecast_url = "https://api.open-meteo.com/v1/forecast"

  def __init__(self, transport=None):
    self.transport = transport or self._request_json

  def fetch(self, destination: str, timeout_seconds: float) -> dict:
    location = self.transport(
      self.geocoding_url,
      {
        "name": destination,
        "count": 1,
        "language": "en",
        "format": "json",
      },
      timeout_seconds,
    )
    results = location.get("results", [])
    if not results:
      return {
        "status": "error",
        "message": f"No location was found for {destination}.",
      }

    match = results[0]
    forecast = self.transport(
      self.forecast_url,
      {
        "latitude": match["latitude"],
        "longitude": match["longitude"],
        "current": "temperature_2m,weather_code",
        "temperature_unit": "celsius",
      },
      timeout_seconds,
    )
    current = forecast.get("current", {})

    return {
      "status": "success",
      "source": "open_meteo",
      "forecast": _weather_code_description(current.get("weather_code")),
      "temperature_c": current.get("temperature_2m"),
    }

  @staticmethod
  def _request_json(url: str, params: dict, timeout_seconds: float) -> dict:
    request = Request(
      f"{url}?{urlencode(params)}",
      headers={"Accept": "application/json"},
    )
    with urlopen(request, timeout=timeout_seconds) as response:
      return json.loads(response.read().decode("utf-8"))


def _weather_code_description(weather_code: int | None) -> str:
  descriptions = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
  }
  return descriptions.get(weather_code, "Unknown conditions")


@dataclass
class WeatherService:
  provider: WeatherProvider
  timeout_seconds: float = 5.0
  max_retries: int = 2
  cache_ttl_seconds: float = 300.0
  clock: object = time.monotonic

  def __post_init__(self):
    self._cache = {}

  def get_weather(self, destination: str) -> dict:
    if not isinstance(destination, str) or not destination.strip():
      return {
        "status": "error",
        "message": "destination is required.",
      }

    normalized_destination = destination.strip()
    now = self.clock()
    cached = self._cache.get(normalized_destination.lower())
    if cached is not None:
      cached_at, cached_response = cached
      if now - cached_at <= self.cache_ttl_seconds:
        return dict(cached_response)
      del self._cache[normalized_destination.lower()]

    attempts = max(1, self.max_retries + 1)

    for attempt in range(attempts):
      try:
        response = self.provider.fetch(
          normalized_destination,
          timeout_seconds=self.timeout_seconds,
        )
      except TimeoutError:
        if attempt == attempts - 1:
          return {
            "status": "error",
            "message": "Weather provider timed out.",
          }
        continue
      except Exception:
        return {
          "status": "error",
          "message": "Weather provider is unavailable.",
        }

      if not isinstance(response, dict):
        return {
          "status": "error",
          "message": "Weather provider returned an invalid response.",
        }

      if response.get("status") == "error":
        return response

      normalized_response = {
        "status": "success",
        "destination": normalized_destination,
        "source": response.get("source", "weather_provider"),
        "forecast": response.get("forecast", "Unknown"),
        "temperature_c": response.get("temperature_c"),
      }
      if self.cache_ttl_seconds > 0:
        self._cache[normalized_destination.lower()] = (
          now,
          normalized_response,
        )
      return normalized_response

    return {
      "status": "error",
      "message": "Weather provider is unavailable.",
    }


def create_weather_service(provider_name: str | None = None) -> WeatherService:
  selected_provider = provider_name or os.getenv("WEATHER_PROVIDER", "demo")
  if selected_provider == "open_meteo":
    provider = OpenMeteoWeatherProvider()
  else:
    provider = DemoWeatherProvider()

  return WeatherService(
    provider=provider,
    timeout_seconds=float(os.getenv("WEATHER_TIMEOUT_SECONDS", "5")),
    max_retries=int(os.getenv("WEATHER_MAX_RETRIES", "2")),
    cache_ttl_seconds=float(os.getenv("WEATHER_CACHE_TTL_SECONDS", "300")),
  )


_weather_service = create_weather_service()


def get_weather(destination: str) -> dict:
  """Returns normalized weather information for a destination."""

  return _weather_service.get_weather(destination)