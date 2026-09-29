# Project Plan

This plan separates verified implementation from future work. It is intentionally more concrete than the original learning outline.

## Implemented

### Foundation

- Python 3.12 and `uv` project setup
- Local dependency management through `pyproject.toml` and `uv.lock`
- Environment template and ignored local secrets
- Root ADK agent with specialist registration

### Agent architecture

- Root concierge routing
- Planning specialist
- Booking specialist
- Pre-trip specialist
- Translation specialist exposed through `AgentTool`
- Sequential and parallel pre-trip orchestration

### Tools and runtime

- Destination information lookup
- Demo weather provider and Open-Meteo adapter
- Trip state save/load tools
- Itinerary artifact save/load tools
- Demo flight and hotel search
- Explicit demo booking confirmation
- In-memory session, memory, artifact, and Runner services

### Reliability and evaluation

- Input validation for core tools
- Provider timeouts, bounded retries, response normalization, and caching
- Structured lifecycle diagnostics
- ADK event tool-call extraction and trace evaluation
- Unit tests for success, invalid input, missing artifacts, provider failures, and approval boundaries

### Documentation

- Setup and usage guide
- FastAPI HTTP wrapper with `/health` and `/chat` endpoints
- Render Blueprint for a demo web service
- System design reference
- Development workflow
- Contribution guide
- Engineering notes
- License
- Local-only verification process with no GitHub Actions

## Near-term plan

1. Keep the local setup and documentation accurate as the code evolves.
2. Add a repeatable before/after translation behavior experiment.
3. Improve trip-state schemas and date/budget normalization.
4. Expand trace evaluations for planning, pre-trip, and artifact workflows.
5. Add deterministic adversarial tests for malformed tool data and prompt-injection-like content.
6. Improve booking approval so confirmation is bound to a server-created option and user approval.

## Medium-term plan

1. Add stronger structured output validation for translation and provider responses.
2. Introduce redacted, structured logging with correlation IDs.
3. Define authenticated user and session boundaries.
4. Replace selected in-memory services with persistent implementations.
5. Add real external APIs behind explicit provider interfaces and mocked tests.
6. Add guardrails, rate limits, cancellation, and operational failure policies.

## Long-term plan

1. Add inspiration, in-trip, and post-trip specialists where they provide real value.
2. Define a stable application/API boundary for a frontend.
3. Decide whether a Node.js or Next.js frontend should call a Python service.
4. Add production deployment documentation and observability.
5. Evaluate A2A or multi-system integration only after the local boundaries are stable.

## Out of scope for now

- GitHub Actions or other hosted CI automation
- Real payments or reservations
- Production authentication and multi-tenant persistence
- A frontend application
- Unbounded autonomous booking

## Definition of done for a roadmap item

A feature is complete when its code, focused tests, failure behavior, documentation, and local verification command agree with each other.
