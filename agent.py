from dotenv import load_dotenv
from google.adk.agents import Agent

from travel_concierge.tools.destination_info import get_destination_info
from travel_concierge.sub_agents.planning.agent import planning_agent
from travel_concierge.sub_agents.booking.agent import booking_agent
from travel_concierge.orchestration.pre_trip_workflow import pre_trip_workflow
from travel_concierge.callbacks import (
  before_agent_callback,
  after_agent_callback,
  before_model_callback,
)

load_dotenv()

root_agent = Agent(
	name="travel_concierge",
	model="gemini-3.5-flash-lite",
	description="A helpful travel concierge.",
	instruction="""
	You are the main travel concierge.

	Understand the user's travel request and delegate the task to the appropriate specialist.

	Use:
	- pre_trip_workflow for preparation before a trip
  - planning_agent for itineraries and trip planning
  - booking_agent for hotel and flight booking information

	Do not attempt to perform a specialist's task yourself
  when a suitable specialist is available.
  """,
	tools=[get_destination_info],
  sub_agents=[
	pre_trip_workflow,
    planning_agent,
    booking_agent,
  ],
	before_agent_callback=before_agent_callback,
	after_agent_callback=after_agent_callback,
	before_model_callback=before_model_callback,
)
