from datetime import datetime


def _validate_destination(destination: str) -> str | None:
  if not isinstance(destination, str) or not destination.strip():
    return "destination is required."
  return None


def _validate_travel_dates(travel_dates: str) -> str | None:
  if not travel_dates:
    return None
  if not isinstance(travel_dates, str):
    return "travel_dates must use YYYY-MM-DD format."
  try:
    datetime.strptime(travel_dates, "%Y-%m-%d")
  except ValueError:
    return "travel_dates must use YYYY-MM-DD format."
  return None


def _validate_budget(budget: str) -> str | None:
  if budget is not None and budget != "" and (
    not isinstance(budget, str) or not budget.strip()
  ):
    return "budget must be a non-empty string when provided."
  return None


def search_flights(destination: str, travel_dates: str = "") -> dict:
  destination_error = _validate_destination(destination)
  if destination_error:
    return {"status": "error", "message": destination_error}

  dates_error = _validate_travel_dates(travel_dates)
  if dates_error:
    return {"status": "error", "message": dates_error}

  return {
    "status": "success",
    "destination": destination.strip(),
    "travel_dates": travel_dates,
    "options": [
      {
        "airline": "Demo Air",
        "price": 450,
        "currency": "USD",
      }
    ],
  }


def search_hotels(destination: str, budget: str = "") -> dict:
  destination_error = _validate_destination(destination)
  if destination_error:
    return {"status": "error", "message": destination_error}

  budget_error = _validate_budget(budget)
  if budget_error:
    return {"status": "error", "message": budget_error}

  return {
    "status": "success",
    "destination": destination.strip(),
    "budget": budget,
    "options": [
      {
        "name": "Demo Central Hotel",
        "price_per_night": 120,
        "currency": "USD",
      }
    ],
  }