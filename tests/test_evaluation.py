from google.adk.events import Event
from google.genai.types import Content, Part

from travel_concierge.evaluation.scenarios import (
  BOOKING_AFTER_APPROVAL,
  BOOKING_WITHOUT_ITINERARY,
  BOOKING_WITH_ITINERARY,
)
from travel_concierge.evaluation.trace import evaluate_tool_trace
from travel_concierge.tools.booking import search_flights
from travel_concierge.tools.booking_confirmation import confirm_booking
from travel_concierge.tools.destination_info import get_destination_info


def make_tool_event(name: str) -> Event:
  return Event(
    author="booking_agent",
    content=Content(
      parts=[Part.from_function_call(name=name, args={})],
    ),
  )


def test_booking_trace_passes_without_confirmation_before_approval():
  result = evaluate_tool_trace(
    [
      make_tool_event("load_itinerary_artifact"),
      make_tool_event("search_flights"),
      make_tool_event("search_hotels"),
    ],
    required_tool_calls=BOOKING_WITH_ITINERARY.required_tool_calls,
    forbidden_tool_calls=BOOKING_WITH_ITINERARY.forbidden_tool_calls,
  )

  assert result.passed
  assert result.tool_calls == (
    "load_itinerary_artifact",
    "search_flights",
    "search_hotels",
  )


def test_booking_without_itinerary_forbids_search_and_confirmation():
  result = evaluate_tool_trace(
    [make_tool_event("load_itinerary_artifact")],
    required_tool_calls=BOOKING_WITHOUT_ITINERARY.required_tool_calls,
    forbidden_tool_calls=BOOKING_WITHOUT_ITINERARY.forbidden_tool_calls,
  )

  assert result.passed


def test_booking_after_approval_requires_confirmation_call():
  result = evaluate_tool_trace(
    [
      make_tool_event("load_itinerary_artifact"),
      make_tool_event("search_flights"),
      make_tool_event("confirm_booking"),
    ],
    required_tool_calls=BOOKING_AFTER_APPROVAL.required_tool_calls,
  )

  assert result.passed


def test_evaluation_reports_missing_and_forbidden_calls():
  result = evaluate_tool_trace(
    [make_tool_event("search_flights")],
    required_tool_calls=("load_itinerary_artifact",),
    forbidden_tool_calls=("search_flights",),
  )

  assert not result.passed
  assert result.missing_required == ("load_itinerary_artifact",)
  assert result.forbidden_present == ("search_flights",)


def test_failure_cases_are_safe():
  assert get_destination_info("Unknown City")["error"]
  assert search_flights("", "2026-10-01")["status"] == "error"
  assert confirm_booking(
    item_type="flight",
    selection={"airline": "Demo Air"},
  )["status"] == "confirmation_required"