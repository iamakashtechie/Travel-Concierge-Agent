from travel_concierge.tools.booking import (
  search_flights,
  search_hotels,
)


def test_search_flights_returns_options():
  result = search_flights("Tokyo", "2026-10-01")

  assert result["status"] == "success"
  assert result["destination"] == "Tokyo"
  assert result["travel_dates"] == "2026-10-01"
  assert result["options"]


def test_search_hotels_returns_options():
  result = search_hotels("Tokyo", "budget")

  assert result["status"] == "success"
  assert result["destination"] == "Tokyo"
  assert result["budget"] == "budget"
  assert result["options"]


def test_search_flights_rejects_missing_destination():
  result = search_flights("")

  assert result["status"] == "error"
  assert result["message"] == "destination is required."


def test_search_flights_rejects_invalid_date():
  result = search_flights("Tokyo", "tomorrow")

  assert result["status"] == "error"
  assert result["message"] == "travel_dates must use YYYY-MM-DD format."


def test_search_hotels_rejects_invalid_budget():
  result = search_hotels("Tokyo", 0)

  assert result["status"] == "error"
  assert result["message"] == "budget must be a non-empty string when provided."