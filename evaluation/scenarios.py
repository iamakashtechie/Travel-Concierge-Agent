from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationScenario:
  name: str
  required_tool_calls: tuple[str, ...] = ()
  forbidden_tool_calls: tuple[str, ...] = ()


BOOKING_WITH_ITINERARY = EvaluationScenario(
  name="booking_with_itinerary",
  required_tool_calls=(
    "load_itinerary_artifact",
    "search_flights",
    "search_hotels",
  ),
  forbidden_tool_calls=("confirm_booking",),
)

BOOKING_WITHOUT_ITINERARY = EvaluationScenario(
  name="booking_without_itinerary",
  required_tool_calls=("load_itinerary_artifact",),
  forbidden_tool_calls=("search_flights", "search_hotels", "confirm_booking"),
)

BOOKING_AFTER_APPROVAL = EvaluationScenario(
  name="booking_after_approval",
  required_tool_calls=(
    "load_itinerary_artifact",
    "search_flights",
    "confirm_booking",
  ),
)