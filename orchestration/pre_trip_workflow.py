from google.adk.agents import Agent, ParallelAgent, SequentialAgent

from travel_concierge.sub_agents.pre_trip.translation import (
  get_common_phrases,
)
from travel_concierge.tools.destination_info import get_destination_info
from travel_concierge.tools.weather import get_weather


destination_research_agent = Agent(
  name="destination_research_agent",
  model="gemini-3.5-flash-lite",
  description="Finds deterministic destination facts for pre-trip research.",
  instruction="""
  Find basic destination facts for the user's requested destination.
  Use get_destination_info and preserve the destination exactly as provided.
  Return only useful destination context for the synthesis agent.
  """,
  tools=[get_destination_info],
  output_key="destination_context",
)


language_research_agent = Agent(
  name="language_research_agent",
  model="gemini-3.5-flash-lite",
  description="Finds local-language phrases for pre-trip research.",
  instruction="""
  Identify the destination's local language and provide useful traveler phrases.
  Call get_common_phrases for the user's destination.
  Return only language context for the synthesis agent.
  """,
  tools=[get_common_phrases],
  output_key="language_context",
)


weather_research_agent = Agent(
  name="weather_research_agent",
  model="gemini-3.5-flash-lite",
  description="Finds normalized weather information for pre-trip research.",
  instruction="""
  Get the current demo/provider weather information for the user's destination.
  Call get_weather and preserve any provider error without inventing a forecast.
  Return only weather context for the synthesis agent.
  """,
  tools=[get_weather],
  output_key="weather_context",
)


pre_trip_research_parallel = ParallelAgent(
  name="pre_trip_research_parallel",
  description="Runs independent destination, language, and weather research in parallel.",
  sub_agents=[
    destination_research_agent,
    language_research_agent,
    weather_research_agent,
  ],
)


pre_trip_synthesis_agent = Agent(
  name="pre_trip_synthesis_agent",
  model="gemini-3.5-flash-lite",
  description="Combines pre-trip research into a practical briefing.",
  instruction="""
  Create a concise pre-trip briefing using the completed research in:
  - destination_context
  - language_context
  - weather_context

  Include practical destination facts, weather, and useful local-language phrases.
  Do not claim that a booking was made or that external research succeeded
  when the research result reports an error.
  """,
)


pre_trip_workflow = SequentialAgent(
  name="pre_trip_workflow",
  description="Runs independent pre-trip research, then synthesizes the result.",
  sub_agents=[
    pre_trip_research_parallel,
    pre_trip_synthesis_agent,
  ],
)