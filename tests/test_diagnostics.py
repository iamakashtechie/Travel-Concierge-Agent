import json

from travel_concierge.callbacks import (
  after_agent_callback,
  before_agent_callback,
  before_model_callback,
)
from travel_concierge.diagnostics import log_event


class FakeCallbackContext:
  agent_name = "booking_agent"
  session_id = "session_1"


class FakeLlmRequest:
  model = "gemini-3.5-flash-lite"


def test_log_event_emits_structured_json(capsys):
  payload = log_event(
    "tool_call",
    {
      "agent_name": "booking_agent",
      "tool_name": "search_flights",
      "status": "success",
    },
  )

  output = capsys.readouterr().out.strip()
  logged_payload = json.loads(output.removeprefix("Event: "))

  assert payload == logged_payload
  assert logged_payload["event_name"] == "tool_call"
  assert logged_payload["agent_name"] == "booking_agent"
  assert logged_payload["tool_name"] == "search_flights"
  assert logged_payload["status"] == "success"
  assert logged_payload["timestamp"]


def test_callbacks_emit_agent_and_model_metadata(capsys):
  context = FakeCallbackContext()

  before_agent_callback(context)
  after_agent_callback(context)
  before_model_callback(context, FakeLlmRequest())

  events = [
    json.loads(line.removeprefix("Event: "))
    for line in capsys.readouterr().out.splitlines()
  ]

  assert events[0]["event_name"] == "before_agent"
  assert events[0]["agent_name"] == "booking_agent"
  assert events[0]["session_id"] == "session_1"
  assert events[1]["event_name"] == "after_agent"
  assert events[2]["event_name"] == "before_model"
  assert events[2]["model_name"] == "gemini-3.5-flash-lite"