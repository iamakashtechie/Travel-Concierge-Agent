# This is an important ADK concept:
# An agent can itself be exposed as a tool to another agent.

# ---------------------------------------------------------------------
# ValueError:
# "additionalProperties" is only supported in Gemini Enterprise
# Agent Platform mode, not in Gemini Developer API mode.

# Why this happened
# We added: output_schema=Translation, to the inner get_common_phrases agent.

# That causes ADK to send a structured-output schema to Gemini. Your local setup is authenticated with a Gemini API key / Developer API, while this particular schema configuration is being rejected in that mode.

# The current Google tooling also distinguishes local Gemini-API development from Google Cloud/Agent Platform deployment.

# So don't switch to Google Cloud just to solve this lab. We're doing the lab locally, and we can make the same architecture work.

# Fix:
# Remove these two things
# Remove:
# output_schema=Translation,
# And because we're no longer enforcing that Pydantic schema, change the instruction slightly.
# ---------------------------------------------------------------------


# from pydantic import BaseModel
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

# class Translation(BaseModel):
#   destination: str
#   language: str
#   phrases: dict[str, str]
  
_translation_agent = Agent(
  name="get_common_phrases",
  model="gemini-3.5-flash-lite",
  description="Provides common phrases in the local language of a travel destination.",
  instruction="""
  Identify the primary local language of the destination.
  
  Then provide 5 to 10 common phrases that would be useful for a traveler.
  
  For each phrase, provide:
  - the phrase in the local language
  - the English translation
  
  Clearly state the destination and local language.
  """,
  # output_schema=Translation
)

get_common_phrases = AgentTool(agent=_translation_agent)