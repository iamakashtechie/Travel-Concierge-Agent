# Travel Concierge

A local Google Agent Development Kit (ADK) multi-agent travel concierge for learning agent delegation, tools, state, memory, artifacts, orchestration, and evaluation.

This repository is a local demonstration project. Flight and hotel results are demo data, confirmation is demo-only, and no payment or real reservation is performed.

## What it does

- Routes requests from a root concierge agent to planning, booking, and pre-trip specialists.
- Runs destination, language, and weather research in parallel before synthesizing a pre-trip briefing.
- Stores current trip details in session state.
- Saves and loads itinerary text as a session artifact.
- Demonstrates cross-session memory retrieval.
- Provides deterministic demo flight, hotel, weather, destination, and confirmation tools.
- Tests routing, state, artifacts, provider failures, callbacks, and tool traces.

## Requirements

- Windows PowerShell, macOS, or Linux
- Python 3.12
- [`uv`](https://docs.astral.sh/uv/)
- A Gemini/Google ADK-compatible local model credential for live agent runs

Python 3.14 may work for some dependencies, but Python 3.12 is the supported project target.

## Setup

From this directory:

```powershell
uv sync --dev
Copy-Item .env.example .env
```

Edit `.env` and add the model credential required by your ADK configuration. Keep `.env` private; it is ignored by Git. The default weather provider is deterministic and does not require an API key.

For a Bash shell, use:

```bash
uv sync --dev
cp .env.example .env
```

## Configuration

`.env.example` documents the supported local settings:

- `GOOGLE_API_KEY`: credential for a Gemini Developer API run, when required by the installed ADK configuration.
- `WEATHER_PROVIDER=demo`: deterministic local weather data.
- `WEATHER_PROVIDER=open_meteo`: use the Open-Meteo adapter.
- `WEATHER_TIMEOUT_SECONDS`: provider request timeout.
- `WEATHER_MAX_RETRIES`: number of timeout retries.
- `WEATHER_CACHE_TTL_SECONDS`: successful weather-response cache lifetime.

Open-Meteo does not require an API key for this adapter.

## Run the tests

Run the complete local suite:

```powershell
uv run pytest
```

Run a focused test file:

```powershell
uv run pytest tests/test_trip_state.py
```

The tests do not require live model calls and cover state, artifacts, booking approval, memory lifecycle, orchestration composition, weather failures, structured diagnostics, and ADK event traces.

## Run the agent

From the project root:

```powershell
uv run adk run .
```

This starts the ADK command-line experience when live model credentials are configured. To inspect the installed CLI options:

```powershell
uv run adk --help
```

The project intentionally has no GitHub Actions workflow. Local tests are the verification path for now.

## Deploy to Render

The repository includes [render.yaml](render.yaml) for a small Render Web Service.

1. Push the repository to GitHub.
2. In Render, choose **New > Blueprint** and select the repository.
3. When prompted, provide `GOOGLE_API_KEY` as a secret environment variable.
4. Deploy the blueprint.
5. Check `https://<your-service>.onrender.com/health`.

The service starts with:

```text
uv run uvicorn app:app --host 0.0.0.0 --port $PORT
```

The API provides:

- `GET /health`: deployment health check.
- `POST /chat`: accepts `{ "message": "...", "session_id": "optional-id" }` and returns the response, session ID, and observed tool calls.

This deployment uses in-memory sessions, memory, and artifacts. They can disappear when the service restarts or sleeps, so this is suitable for a demo rather than production persistence. Render supplies `PORT`; do not hard-code it.

## Project structure

```text
travel_concierge/
├── agent.py                    # Root agent and specialist registration
├── runtime.py                  # Session, memory, artifact, and Runner services
├── callbacks.py                # Runtime lifecycle callbacks
├── diagnostics.py              # Structured event logging
├── orchestration/
│   └── pre_trip_workflow.py    # Parallel research and sequential synthesis
├── sub_agents/
│   ├── booking/                # Demo booking specialist
│   ├── planning/               # Itinerary and memory specialist
│   └── pre_trip/               # Language and preparation specialist
├── tools/                      # Deterministic domain operations
├── evaluation/                 # Trace contracts and scenarios
├── demo/                       # Small standalone ADK experiments
├── tests/                      # Unit and behavior-focused tests
├── README.md                   # Setup and quick reference
├── SYSTEM_DESIGN.md            # Architecture and boundaries
├── WORKFLOW.md                 # Development and verification process
├── CONTRIBUTING.md             # Contribution standards
├── PLAN.md                     # Implemented work and future roadmap
├── NOTES.md                    # Durable engineering notes
└── LICENSE                    # MIT license
```

## Documentation map

- [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md): components, data flow, state, and boundaries.
- [WORKFLOW.md](WORKFLOW.md): setup, run, test, and development loops.
- [CONTRIBUTING.md](CONTRIBUTING.md): coding, testing, and review expectations.
- [PLAN.md](PLAN.md): what is implemented and what comes next.
- [NOTES.md](NOTES.md): concepts and decisions worth preserving.

## Safety boundaries

- Booking tools return demo options only.
- Confirmation is explicitly demo-only.
- No real reservation or payment is performed.
- External providers are isolated behind injectable interfaces and tested with deterministic substitutes.
- The default runtime uses in-memory services and is not a production multi-user deployment.

## License

This project is released under the [MIT License](LICENSE).
