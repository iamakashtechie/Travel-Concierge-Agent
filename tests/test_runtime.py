from unittest.mock import AsyncMock

import pytest
from google.adk.events import Event
from google.genai.types import Content, Part

from travel_concierge.runtime import TravelConciergeRuntime


@pytest.mark.anyio
async def test_runtime_creates_session_with_state():
  runtime = TravelConciergeRuntime(user_id="akash")

  session = await runtime.create_session(
    session_id="session_1",
    state={"trip_details": {"destination": "Tokyo"}},
  )

  assert session.id == "session_1"
  assert session.state["trip_details"]["destination"] == "Tokyo"


def test_runtime_runner_shares_memory_and_artifact_services():
  runtime = TravelConciergeRuntime()

  runner = runtime.create_runner()

  assert runner.memory_service is runtime.memory_service
  assert runner.artifact_service is runtime.artifact_service
  assert runner.session_service is runtime.session_service


@pytest.mark.anyio
async def test_archive_session_adds_completed_session_to_memory():
  runtime = TravelConciergeRuntime()
  await runtime.create_session("session_1")
  runtime.memory_service.add_session_to_memory = AsyncMock()

  result = await runtime.archive_session("session_1")

  assert result == {
    "status": "success",
    "session_id": "session_1",
  }
  runtime.memory_service.add_session_to_memory.assert_awaited_once()


@pytest.mark.anyio
async def test_archive_session_reports_missing_session():
  runtime = TravelConciergeRuntime()

  result = await runtime.archive_session("missing")

  assert result["status"] == "not_found"


@pytest.mark.anyio
async def test_archived_session_can_be_retrieved_by_memory_search():
  runtime = TravelConciergeRuntime(user_id="akash")
  session = await runtime.create_session("session_1")
  await runtime.session_service.append_event(
    session,
    Event(
      author="user",
      content=Content(
        role="user",
        parts=[Part(text="I prefer minimal walking in Tokyo.")],
      ),
    )
  )

  result = await runtime.archive_session("session_1")
  memories = await runtime.memory_service.search_memory(
    app_name=runtime.app_name,
    user_id=runtime.user_id,
    query="Tokyo walking preference",
  )

  assert result["status"] == "success"
  assert len(memories.memories) == 1
  assert memories.memories[0].content.parts[0].text == (
    "I prefer minimal walking in Tokyo."
  )