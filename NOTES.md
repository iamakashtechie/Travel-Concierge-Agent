# Engineering Notes

## Project purpose

This repository is a practical ADK learning project. The travel domain is a concrete setting for understanding multi-agent design rather than the end goal by itself.

## Core concepts

### Session, state, memory, and context

- **Session:** one conversation thread and its event history.
- **State:** structured, current values for the active conversation, such as destination and trip duration.
- **Memory:** information archived from earlier sessions and retrieved when relevant.
- **Artifact:** file-like content, such as a saved itinerary.
- **Context:** runtime capabilities available to a tool or callback, including session state and artifact services.

Current session state should take precedence over older memory when they conflict.

### Agent types

- A deterministic Python function is a **tool**.
- A specialist ADK `Agent` delegates reasoning to a focused role.
- An `AgentTool` exposes one agent as a callable capability for another agent.
- A `SequentialAgent` or `ParallelAgent` composes execution without putting all orchestration logic in one prompt.

## Decisions

1. Keep persistence and validation in Python tools.
2. Keep specialist reasoning in narrowly scoped agents.
3. Use demo booking data until a real integration has an explicit design and approval boundary.
4. Keep weather behind a provider interface so tests can remain deterministic.
5. Prefer event and tool-trace assertions over judging only the final natural-language response.
6. Use in-memory ADK services while learning; defer database and tenancy choices until an application boundary is needed.

## Current implementation notes

- The planning agent saves itinerary content through the artifact service.
- The booking agent loads an itinerary before searching demo options.
- Booking confirmation requires an explicit approval value in the current demo contract, but stronger server-side approval tokens remain future hardening work.
- Translation is implemented as an `AgentTool`; strict structured output is currently disabled for the local Developer API configuration.
- Open-Meteo access has bounded timeout retries and short-lived successful-response caching.

## Working assumptions

- Tests run from the repository root with `uv run pytest`.
- Python 3.12 is the supported interpreter.
- `.env` is local configuration and must never be committed.
- No GitHub Actions workflow is part of the current project process.

## Open questions

- Which persistent session and artifact store should be used beyond local experiments?
- What authentication and tenant model should protect sessions and memory?
- Should a future frontend call Python directly, through an HTTP service, or through a separate Node.js boundary?
- Which provider contracts are stable enough to support real integrations?
