from dataclasses import dataclass, field

from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content

from travel_concierge.agent import root_agent


@dataclass
class TravelConciergeRuntime:
  """Owns the services required by a memory-enabled concierge session."""

  app_name: str = "travel_concierge"
  user_id: str = "user"
  session_service: InMemorySessionService = field(
    default_factory=InMemorySessionService,
  )
  memory_service: InMemoryMemoryService = field(
    default_factory=InMemoryMemoryService,
  )
  artifact_service: InMemoryArtifactService = field(
    default_factory=InMemoryArtifactService,
  )

  def create_runner(self) -> Runner:
    return Runner(
      agent=root_agent,
      app_name=self.app_name,
      session_service=self.session_service,
      memory_service=self.memory_service,
      artifact_service=self.artifact_service,
    )

  async def create_session(
    self,
    session_id: str,
    state: dict | None = None,
  ):
    return await self.session_service.create_session(
      app_name=self.app_name,
      user_id=self.user_id,
      session_id=session_id,
      state=state,
    )

  async def run_turn(
    self,
    session_id: str,
    message: Content,
  ) -> list:
    """Runs one turn and returns its events without archiving the session."""

    session = await self.session_service.get_session(
      app_name=self.app_name,
      user_id=self.user_id,
      session_id=session_id,
    )
    if session is None:
      await self.create_session(session_id)

    events = []
    async for event in self.create_runner().run_async(
      user_id=self.user_id,
      session_id=session_id,
      new_message=message,
    ):
      events.append(event)
    return events

  async def archive_session(self, session_id: str) -> dict:
    """Adds a completed session to memory for future conversations."""

    session = await self.session_service.get_session(
      app_name=self.app_name,
      user_id=self.user_id,
      session_id=session_id,
    )
    if session is None:
      return {
        "status": "not_found",
        "message": f"Session '{session_id}' was not found.",
      }

    await self.memory_service.add_session_to_memory(session)
    return {
      "status": "success",
      "session_id": session_id,
    }