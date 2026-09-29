from google.adk.tools import ToolContext
import google.genai.types as types

from travel_concierge.diagnostics import log_event

def save_trip_details(
  destination: str,
  duration_days: int,
  interests: str,
  walking_preferences: str,
  travelers: int = 1,
  travel_dates: str = "",
  budget: str = "",
  accommodation_preferences: str = "",
  tool_context: ToolContext = None,
) -> dict:
  """Saves the user's trip details for this conversation.
  
  Args:
    destination: Travel destination.
    duration_days: Number of days in the trip.
    interests: Main interests for the trip.
    walking_preferences: How much walking the traveler prefers.
    travelers: Number of travelers.
    travel_dates: Travel dates, if known.
    budget: Approximate accommodation/trip budget, if known.
    accommodation_preference: Preferred accommodation type, if known.
    
  Returns:
    Confirmation that the trip details were saved.
  """

  log_event(
    "save_trip_details:start",
    {
      "destination": destination,
      "duration_days": duration_days,
      "interests": interests,
      "travelers": travelers,
    },
  )
  
  if tool_context is None:
    return {
      "status": "error",
      "message": "Tool context is required to save trip details."
    }

  try:
    _validate_trip_fields(
      destination=destination,
      duration_days=duration_days,
      interests=interests,
      walking_preferences=walking_preferences,
      travelers=travelers,
    )

  except ValueError as exc:
    return {
      "status": "error",
      "message": str(exc)
    }

  tool_context.state["trip_details"] = {
      "destination": destination.strip(),
      "duration_days": duration_days,
      "interests": interests.strip(),
      "walking_preferences": walking_preferences.strip(),
      "travelers": travelers,
      "travel_dates": travel_dates.strip() if travel_dates else None,
      "budget": budget.strip() if budget else None,
      "accommodation_preferences": accommodation_preferences.strip() if accommodation_preferences else None,
  }

  log_event("save_trip_details:success", {"trip_details": tool_context.state["trip_details"]})
  
  return {
    "status": "success",
    "message": "Trip details are saved."
  }
  
def get_trip_details (tool_context: ToolContext) -> dict:
  """Retrives saved trip details from the current session."""
  
  details = tool_context.state.get("trip_details")
  
  if details is None:
    return {
      "status": "not_found",
      "message": "No trip details have been set yet."
    }
    
  return {
    "status": "success",
    "trip_details": details
  }
  
def _validate_trip_fields(
  destination: str,
  duration_days: int,
  interests: str,
  walking_preferences: str,
  travelers: int,
) -> None:
  """Validates the required trip fields."""

  if not isinstance(destination, str) or not destination.strip():
    raise ValueError("destination is required.")

  if not isinstance(interests, str) or not interests.strip():
    raise ValueError("interests is required.")

  if not isinstance(walking_preferences, str) or not walking_preferences.strip():
    raise ValueError("walking_preferences is required.")

  if type(duration_days) is not int or duration_days <= 0:
    raise ValueError("duration_days must be a positive integer.")

  if type(travelers) is not int or travelers <= 0:
    raise ValueError("travelers must be a positive integer.")

def _validate_filename(filename: str) -> str:
  """Validates the filename for the itinerary artifact."""
  
  cleaned = (filename or "trip_itinerary.txt").strip()
  if not cleaned:
    return "trip_itinerary.txt"
  if "/" in cleaned or "\\" in cleaned:
    raise ValueError("filename must be a simple file name, not a path.")
  return cleaned

async def save_itinerary_artifact(
  itinerary_text: str | None = None,
  content: str | None = None,
  filename: str = "trip_itinerary.txt",
  tool_context: ToolContext = None,
) -> dict:
  """Saves an itinerary as a text artifact for the active session."""

  log_event("save_itinerary_artifact:start", {"filename": filename})
  
  if tool_context is None:
    return {
      "status": "error",
      "message": "Tool context is required to save itinerary artifact."
    }
    
  text = itinerary_text if itinerary_text is not None else content
  
  if not text or not text.strip():
    return {
      "status": "error",
      "message": "Itinerary text is empty."
    }

  safe_filename = _validate_filename(filename)
    
  artifact = types.Part.from_bytes(
    data=text.encode("utf-8"),
    mime_type="text/plain",
  )
  
  version = await tool_context.save_artifact(
    artifact=artifact,
    filename=safe_filename,
  )

  log_event("save_itinerary_artifact:success", {"filename": filename, "version": version})
  
  return {
    "status": "success",
    "filename": safe_filename,
    "version": version
  }
  
async def load_itinerary_artifact(
  filename: str = "trip_itinerary.txt",
  tool_context: ToolContext = None,
) -> dict:
  """Loads an itinerary artifact from the active session."""

  log_event("load_itinerary_artifact:start", {"filename": filename})

  if tool_context is None:
    return {
      "status": "error",
      "message": "Tool context is required to load itinerary artifact."
    }

  safe_filename = _validate_filename(filename)
    
  artifact = await tool_context.load_artifact(filename=safe_filename)
  
  if artifact is None:
    return {
      "status": "not_found",
      "message": f"The itinerary artifact '{safe_filename}' was not found.",
    }
    
  if artifact.inline_data is None:
    return {
      "status": "error",
      "message": "The artifact does not contain inline data.",
    }

  log_event("load_itinerary_artifact:success", {"filename": filename})
  
  return {
    "status": "success",
    "filename": safe_filename,
    "content": artifact.inline_data.data.decode("utf-8"),
    "mime_type": artifact.inline_data.mime_type,
  }

