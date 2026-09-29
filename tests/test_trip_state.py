import asyncio

import pytest

from travel_concierge.tools.trip_state import (
  get_trip_details,
  load_itinerary_artifact,
  save_itinerary_artifact,
  save_trip_details,
)


class FakeToolContext:
  def __init__(self):
    self.state = {}
    self.artifacts = {}

  async def save_artifact(self, artifact, filename):
    self.artifacts[filename] = artifact
    return 0

  async def load_artifact(self, filename):
    return self.artifacts.get(filename)

class MalformedArtifact:
  inline_data = None

def test_save_and_get_trip_details():
  context = FakeToolContext()

  result = save_trip_details(
    destination="Tokyo",
    duration_days=5,
    interests="history and culture",
    walking_preferences="minimal walking",
    travelers=2,
    accommodation_preferences="hotel",
    tool_context=context,
  )

  assert result["status"] == "success"
  assert context.state["trip_details"]["destination"] == "Tokyo"
  assert (
    context.state["trip_details"]["accommodation_preferences"]
    == "hotel"
  )

  saved = get_trip_details(context)

  assert saved["status"] == "success"
  assert saved["trip_details"]["duration_days"] == 5


def test_save_trip_details_rejects_missing_destination():
  context = FakeToolContext()

  result = save_trip_details(
    destination="",
    duration_days=5,
    interests="history",
    walking_preferences="minimal walking",
    tool_context=context,
  )

  assert result["status"] == "error"
  assert "destination is required" in result["message"]


def test_save_trip_details_rejects_invalid_duration():
  context = FakeToolContext()

  result = save_trip_details(
    destination="Tokyo",
    duration_days=0,
    interests="history",
    walking_preferences="minimal walking",
    tool_context=context,
  )

  assert result["status"] == "error"
  assert "duration_days must be a positive integer" in result["message"]


def test_save_trip_details_rejects_non_integer_duration():
  context = FakeToolContext()

  result = save_trip_details(
    destination="Tokyo",
    duration_days="five",
    interests="history",
    walking_preferences="minimal walking",
    tool_context=context,
  )

  assert result["status"] == "error"
  assert "duration_days must be a positive integer" in result["message"]


def test_save_trip_details_rejects_invalid_travelers():
  context = FakeToolContext()

  result = save_trip_details(
    destination="Tokyo",
    duration_days=5,
    interests="history",
    walking_preferences="minimal walking",
    travelers=0,
    tool_context=context,
  )

  assert result["status"] == "error"
  assert "travelers must be a positive integer" in result["message"]


def test_save_trip_details_rejects_non_integer_travelers():
  context = FakeToolContext()

  result = save_trip_details(
    destination="Tokyo",
    duration_days=5,
    interests="history",
    walking_preferences="minimal walking",
    travelers=1.5,
    tool_context=context,
  )

  assert result["status"] == "error"
  assert "travelers must be a positive integer" in result["message"]


def test_save_itinerary_rejects_empty_content():
  context = FakeToolContext()

  result = asyncio.run(
    save_itinerary_artifact(
      itinerary_text="",
      tool_context=context,
    )
  )

  assert result["status"] == "error"
  assert result["message"] == "Itinerary text is empty."


def test_save_itinerary_rejects_path_filename():
  context = FakeToolContext()

  with pytest.raises(ValueError, match="simple file name"):
    asyncio.run(
      save_itinerary_artifact(
        itinerary_text="Day 1: Tokyo",
        filename="../trip_itinerary.txt",
        tool_context=context,
      )
    )

def test_save_and_load_itinerary_artifact():
  context = FakeToolContext()

  save_result = asyncio.run(
    save_itinerary_artifact(
      itinerary_text="Day 1: Tokyo",
      tool_context=context,
    )
  )

  assert save_result["status"] == "success"

  load_result = asyncio.run(
    load_itinerary_artifact(tool_context=context)
  )

  assert load_result["status"] == "success"
  assert load_result["content"] == "Day 1: Tokyo"


def test_load_itinerary_returns_not_found_for_missing_artifact():
  context = FakeToolContext()

  result = asyncio.run(
    load_itinerary_artifact(tool_context=context)
  )

  assert result["status"] == "not_found"


def test_load_itinerary_rejects_malformed_artifact():
  context = FakeToolContext()
  context.artifacts["trip_itinerary.txt"] = MalformedArtifact()

  result = asyncio.run(
    load_itinerary_artifact(tool_context=context)
  )

  assert result["status"] == "error"
  assert result["message"] == "The artifact does not contain inline data."