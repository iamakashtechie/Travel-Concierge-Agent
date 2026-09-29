from google.adk.agents import Agent

from travel_concierge.sub_agents.pre_trip.translation import (
  get_common_phrases,
)

pre_trip_agent = Agent(
  name="pre_trip_agent",
  model="gemini-3.5-flash-lite",
  description="Provides useful information before a trip.",
  instruction="""
  You are a pre-trip travel assistant.
  
  Help travelers prepare for the trip.
  
  Provide useful information about:
  - local language
  - currency
  - cultural considerations
  - useful travel tips
  - what the traveler should know before arriving
  
  When the user asks about the local language, call the tool get_common_phrases to provide useful phrases in the destination's local language.
  """,
  tools=[get_common_phrases],
)