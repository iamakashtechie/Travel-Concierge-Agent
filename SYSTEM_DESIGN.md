# System Design

## Purpose

Travel Concierge is a local Google Agent Development Kit (ADK) learning project. It demonstrates how a root agent delegates travel work to specialist agents and deterministic Python tools.

The current implementation is intentionally local and demo-safe. It does not make real reservations, process payments, or provide production-grade multi-user storage.

## HTTP deployment boundary

`app.py` is a thin FastAPI boundary around `TravelConciergeRuntime`:

```text
HTTP client
  |
  +--> GET /health
  |
  +--> POST /chat
          |
          v
  TravelConciergeRuntime
          |
          v
      root_agent
```

The API creates a session ID when one is not supplied and returns the final response plus observed tool-call names. It does not expose raw ADK events or credentials. The Render configuration in `render.yaml` uses Uvicorn and Render's `$PORT`.

## Runtime shape

```text
User
  |
  v
travel_concierge (root agent)
  |
  +--> pre_trip_workflow
  |      |
  |      +--> parallel destination research
  |      +--> parallel language research
  |      +--> parallel weather research
  |      +--> synthesis agent
  |
  +--> planning_agent
  |      +--> session trip state
  |      +--> itinerary artifact
  |      +--> memory lookup
  |
  +--> booking_agent
         +--> saved trip details
         +--> saved itinerary
         +--> demo flight and hotel search
         +--> explicit demo confirmation
```

## Component responsibilities

### Root agent

`agent.py` is responsible for intent recognition and delegation. It owns the specialist-agent registry and should not implement specialist workflows itself.

### Specialist agents

- `sub_agents/planning/agent.py` creates and retrieves itineraries.
- `sub_agents/booking/agent.py` searches demo options and enforces the conversation-level approval policy.
- `sub_agents/pre_trip/agent.py` provides local-language preparation.
- `orchestration/pre_trip_workflow.py` composes parallel research followed by synthesis.

### Deterministic tools

The `tools/` package owns predictable operations:

- destination lookup
- weather provider access
- trip state persistence
- artifact persistence
- demo flight and hotel search
- demo booking confirmation

A tool should validate its inputs and return an explicit status rather than relying on the model to interpret exceptions.

### Runtime services

`runtime.py` assembles ADK `Runner`, session, memory, and artifact services. The default services are in-memory and are intended for local learning and tests.

## Data flow

1. A user message enters the root agent.
2. The root agent transfers the request to a specialist.
3. The specialist may call deterministic tools or an `AgentTool`.
4. Tools read or update session state and artifacts through `ToolContext`.
5. ADK emits events for model calls, tool calls, delegation, and final responses.
6. Tests inspect tool traces and deterministic results where possible.

## State boundaries

- **Session:** one active conversation and its event history.
- **Session state:** structured, current trip details.
- **Memory:** information archived from earlier sessions for later retrieval.
- **Artifact:** file-like itinerary content associated with a session.
- **Context:** runtime capabilities supplied to a tool or callback.

Current state is authoritative for the active trip. Memory is supplemental and must not silently replace current user input.

## Failure boundaries

External weather access is isolated behind `WeatherProvider`. The service applies timeouts, bounded retries, response normalization, and a short-lived cache. Booking and payment remain deterministic demo tools.

Failures should be returned as structured tool errors. Agents must not claim that an external lookup or booking succeeded when a tool reports failure.

## Current limitations

- Services are in memory and do not survive process restarts.
- Booking confirmation is demo-only.
- Translation output is natural-language text rather than an enforced schema in the local Developer API configuration.
- Authentication, authorization, rate limiting, and persistent tenancy are not implemented.
- There is no web frontend; `app.py` provides only a minimal HTTP API for deployment demos.

These limitations are tracked in [PLAN.md](PLAN.md).
