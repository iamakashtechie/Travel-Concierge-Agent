import json
from datetime import datetime, timezone


def log_event(event_name: str, details: dict | None = None) -> dict:
  """Print and return a machine-readable runtime event."""

  payload = {
    "event_name": event_name,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    **(details or {}),
  }
  print(f"Event: {json.dumps(payload, sort_keys=True, default=str)}")
  return payload