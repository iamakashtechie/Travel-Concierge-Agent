from dataclasses import dataclass

from travel_concierge.tools.weather import (
  OpenMeteoWeatherProvider,
  WeatherService,
  create_weather_service,
  get_weather,
)


@dataclass
class SuccessfulProvider:
  calls: int = 0

  def fetch(self, destination: str, timeout_seconds: float) -> dict:
    self.calls += 1
    return {
      "status": "success",
      "source": "test_provider",
      "forecast": f"Clear in {destination}",
      "temperature_c": 20,
    }


class TimeoutProvider:
  def __init__(self):
    self.calls = 0

  def fetch(self, destination: str, timeout_seconds: float) -> dict:
    self.calls += 1
    raise TimeoutError


class BrokenProvider:
  def fetch(self, destination: str, timeout_seconds: float) -> dict:
    raise RuntimeError("provider failure")


def test_demo_weather_returns_normalized_data():
  result = get_weather("Tokyo")

  assert result["status"] == "success"
  assert result["destination"] == "Tokyo"
  assert result["source"] == "demo_weather_provider"
  assert result["temperature_c"] == 19


def test_weather_rejects_missing_destination():
  result = get_weather("")

  assert result["status"] == "error"
  assert result["message"] == "destination is required."


def test_weather_retries_timeout_then_returns_error():
  provider = TimeoutProvider()
  service = WeatherService(provider=provider, max_retries=2)

  result = service.get_weather("Tokyo")

  assert result["status"] == "error"
  assert result["message"] == "Weather provider timed out."
  assert provider.calls == 3


def test_weather_returns_provider_unavailable_for_unexpected_failure():
  result = WeatherService(provider=BrokenProvider()).get_weather("Tokyo")

  assert result["status"] == "error"
  assert result["message"] == "Weather provider is unavailable."


def test_weather_normalizes_provider_response():
  provider = SuccessfulProvider()

  result = WeatherService(provider=provider).get_weather(" Tokyo ")

  assert result == {
    "status": "success",
    "destination": "Tokyo",
    "source": "test_provider",
    "forecast": "Clear in Tokyo",
    "temperature_c": 20,
  }
  assert provider.calls == 1


def test_weather_caches_successful_response_until_ttl_expires():
  provider = SuccessfulProvider()
  current_time = [100.0]
  service = WeatherService(
    provider=provider,
    cache_ttl_seconds=10,
    clock=lambda: current_time[0],
  )

  first = service.get_weather("Tokyo")
  second = service.get_weather("tokyo")
  current_time[0] = 111.0
  third = service.get_weather("Tokyo")

  assert first == second
  assert third == first
  assert provider.calls == 2


def test_open_meteo_provider_uses_geocoding_and_forecast_transport():
  requests = []

  def transport(url, params, timeout_seconds):
    requests.append((url, params, timeout_seconds))
    if "geocoding" in url:
      return {
        "results": [
          {"latitude": 52.37, "longitude": 4.90},
        ],
      }
    return {
      "current": {
        "temperature_2m": 16,
        "weather_code": 2,
      },
    }

  provider = OpenMeteoWeatherProvider(transport=transport)
  result = WeatherService(provider=provider).get_weather("Amsterdam")

  assert result == {
    "status": "success",
    "destination": "Amsterdam",
    "source": "open_meteo",
    "forecast": "Partly cloudy",
    "temperature_c": 16,
  }
  assert len(requests) == 2
  assert requests[0][1]["name"] == "Amsterdam"
  assert requests[1][1]["latitude"] == 52.37


def test_open_meteo_provider_reports_unknown_location():
  provider = OpenMeteoWeatherProvider(
    transport=lambda url, params, timeout_seconds: {"results": []},
  )

  result = WeatherService(provider=provider).get_weather("Unknown City")

  assert result["status"] == "error"
  assert "No location was found" in result["message"]


def test_weather_service_can_be_selected_from_configuration(monkeypatch):
  monkeypatch.setenv("WEATHER_PROVIDER", "open_meteo")

  service = create_weather_service()

  assert isinstance(service.provider, OpenMeteoWeatherProvider)