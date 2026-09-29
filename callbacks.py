from travel_concierge.diagnostics import log_event


def log_runtime_event(stage: str, **metadata) -> dict:
  return log_event(stage, metadata)

def before_agent_callback(callback_context, **kwargs):
  log_runtime_event(
      "before_agent",
      agent_name=getattr(callback_context, "agent_name", "unknown"),
      session_id=getattr(callback_context, "session_id", "unknown"),
    )

def after_agent_callback(callback_context, **kwargs):
  log_runtime_event(
    "after_agent",
    agent_name=getattr(callback_context, "agent_name", "unknown"),
    session_id=getattr(callback_context, "session_id", "unknown"),
  )

def before_model_callback(callback_context, llm_request, **kwargs):
  log_runtime_event(
    "before_model",
    agent_name=getattr(callback_context, "agent_name", "unknown"),
    model_name=getattr(llm_request, "model", "unknown"),
  )