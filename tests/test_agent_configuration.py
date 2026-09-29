from google.adk.agents import ParallelAgent, SequentialAgent

from travel_concierge.agent import root_agent
from travel_concierge.sub_agents.booking.agent import booking_agent
from travel_concierge.orchestration.pre_trip_workflow import (
  pre_trip_research_parallel,
  pre_trip_synthesis_agent,
  pre_trip_workflow,
)
from travel_concierge.sub_agents.planning.agent import planning_agent


def get_tool_names(agent):
  names = []

  for tool in agent.tools:
    name = getattr(tool, "name", None)

    if name is None:
      name = getattr(tool, "__name__", None)

    if name is not None:
      names.append(name)

  return names


def test_planning_agent_has_itinerary_tools():
  tool_names = get_tool_names(planning_agent)

  assert "save_trip_details" in tool_names
  assert "get_trip_details" in tool_names
  assert "save_itinerary_artifact" in tool_names
  assert "load_itinerary_artifact" in tool_names


def test_booking_agent_has_booking_tools():
  tool_names = get_tool_names(booking_agent)

  assert "get_trip_details" in tool_names
  assert "load_itinerary_artifact" in tool_names
  assert "search_flights" in tool_names
  assert "search_hotels" in tool_names
  assert "confirm_booking" in tool_names


def test_pre_trip_workflow_is_sequential_over_parallel_research():
  assert isinstance(pre_trip_workflow, SequentialAgent)
  assert pre_trip_workflow.sub_agents == [
    pre_trip_research_parallel,
    pre_trip_synthesis_agent,
  ]
  assert isinstance(pre_trip_research_parallel, ParallelAgent)
  assert [
    agent.name for agent in pre_trip_research_parallel.sub_agents
  ] == [
    "destination_research_agent",
    "language_research_agent",
    "weather_research_agent",
  ]


def test_root_agent_registers_pre_trip_workflow():
  sub_agent_names = [agent.name for agent in root_agent.sub_agents]

  assert "pre_trip_workflow" in sub_agent_names


def test_booking_agent_has_failure_and_approval_policy():
  assert "If the itinerary is missing or loading it fails" in booking_agent.instruction
  assert "If a search tool returns an error" in booking_agent.instruction
  assert "explicit user confirmation" in booking_agent.instruction