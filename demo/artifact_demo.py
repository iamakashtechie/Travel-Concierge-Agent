import asyncio

from dotenv import load_dotenv
import google.genai.types as types

from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools import ToolContext
from google.genai.types import Content, Part


load_dotenv()


APP_NAME = "artifact_demo"
USER_ID = "akash"
SESSION_ID = "artifact_session"
MODEL = "gemini-3.5-flash-lite"


async def save_itinerary(
  tool_context: ToolContext,
) -> dict:
  """Creates and saves a simple text itinerary as an artifact."""

  itinerary_text = """
  Tokyo 5-Day Itinerary

	Day 1:
	- Asakusa
	- Senso-ji Temple
	- Nakamise Street

	Day 2:
	- Tokyo National Museum
	- Ueno Park

	Day 3:
	- Meiji Shrine
	- Harajuku
	- Shibuya

	Day 4:
	- Imperial Palace area
	- Ginza

	Day 5:
	- Odaiba
	- Tokyo waterfront
	"""

  artifact = types.Part.from_bytes(
    data=itinerary_text.encode("utf-8"),
    mime_type="text/plain",
  )

  version = await tool_context.save_artifact(
		filename="tokyo_itinerary.txt",
		artifact=artifact,
  )

  return {
    "status": "success",
    "filename": "tokyo_itinerary.txt",
    "version": version,
  }


async def load_itinerary(
    tool_context: ToolContext,
) -> dict:
  """Loads the saved Tokyo itinerary artifact."""

  artifact = await tool_context.load_artifact(
    filename="tokyo_itinerary.txt"
  )

  if artifact is None:
    return {
      "status": "not_found",
      "message": "The itinerary artifact was not found.",
    }

  if artifact.inline_data is None:
    return {
      "status": "error",
      "message": "The artifact does not contain inline data.",
    }

  itinerary_text = artifact.inline_data.data.decode("utf-8")

  return {
    "status": "success",
    "filename": "tokyo_itinerary.txt",
    "content": itinerary_text,
    "mime_type": artifact.inline_data.mime_type,
  }


agent = Agent(
  name="artifact_agent",
  model=MODEL,
  instruction="""
  You are an artifact demonstration agent.

  When the user asks you to create the itinerary file,
  call save_itinerary.

  When the user asks you to read or retrieve the saved
  itinerary file, call load_itinerary.

  After the tool succeeds, clearly report the result.
  """,
  tools=[
    save_itinerary,
    load_itinerary,
  ],
)


async def main():
  # Create the services.
  session_service = InMemorySessionService()
  artifact_service = InMemoryArtifactService()

  # Create one session.
  await session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
  )

  # Create the runner.
  runner = Runner(
    agent=agent,
    app_name=APP_NAME,
    session_service=session_service,
    artifact_service=artifact_service,
  )

  # =====================================================
  # TURN 1 — SAVE ARTIFACT
  # =====================================================

  print("\n===== TURN 1: SAVE ARTIFACT =====\n")

  message1 = Content(
    role="user",
    parts=[
      Part(
        text="Create the Tokyo itinerary file."
      )
    ],
  )

  async for event in runner.run_async(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=message1,
  ):
    if event.is_final_response():
      if event.content and event.content.parts:
        print(event.content.parts[0].text)

  # =====================================================
  # TURN 2 — LOAD ARTIFACT
  # =====================================================

  print("\n===== TURN 2: LOAD ARTIFACT =====\n")

  message2 = Content(
    role="user",
    parts=[
      Part(
        text="Read back the Tokyo itinerary file you saved."
      )
    ],
  )

  async for event in runner.run_async(
    user_id=USER_ID,
    session_id=SESSION_ID,
    new_message=message2,
  ):
    if event.is_final_response():
      if event.content and event.content.parts:
        print(event.content.parts[0].text)


if __name__ == "__main__":
  asyncio.run(main())