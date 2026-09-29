from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field
from google.genai.types import Content, Part

from travel_concierge.evaluation.trace import extract_tool_calls
from travel_concierge.runtime import TravelConciergeRuntime


app = FastAPI(
  title="Travel Concierge API",
  version="0.1.0",
  description="HTTP wrapper for the local Travel Concierge ADK agent.",
)
runtime = TravelConciergeRuntime(user_id="render-demo-user")


class ChatRequest(BaseModel):
  message: str = Field(min_length=1, max_length=4000)
  session_id: str | None = Field(default=None, min_length=1, max_length=128)


class ChatResponse(BaseModel):
  session_id: str
  response: str
  tool_calls: list[str]


@app.get("/health")
async def health() -> dict[str, str]:
  return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
  session_id = request.session_id or str(uuid4())
  events = await runtime.run_turn(
    session_id=session_id,
    message=Content(
      role="user",
      parts=[Part(text=request.message)],
    ),
  )

  response_text = ""
  for event in events:
    if not event.is_final_response():
      continue
    content = getattr(event, "content", None)
    for part in getattr(content, "parts", []) or []:
      text = getattr(part, "text", None)
      if text:
        response_text = text

  return ChatResponse(
    session_id=session_id,
    response=response_text or "The agent did not return a final response.",
    tool_calls=list(extract_tool_calls(events)),
  )