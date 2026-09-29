# Development Workflow

## First-time setup

1. Install Python 3.12 and `uv`.
2. From this directory, create the environment and install dependencies:

   ```powershell
   uv sync --dev
   ```

3. Copy `.env.example` to `.env` and add local model credentials if you want to run Gemini-backed agents.
4. Run the tests before making changes:

   ```powershell
   uv run pytest
   ```

## Typical development loop

1. Read the owning agent or tool and its nearest test.
2. Make the smallest behavior-focused change.
3. Run the narrowest relevant test first.
4. Run the complete suite before sharing the change.
5. Update the relevant documentation when behavior or setup changes.

## Running the agent

From the project root:

```powershell
uv run adk run .
```

Use the ADK web interface when you need to inspect event traces and delegation. The exact command may vary with the installed ADK version; `uv run adk --help` shows the available commands.

## Useful checks

```powershell
uv run pytest
uv run pytest tests/test_trip_state.py
uv run pytest tests/test_weather.py
uv run python -m compileall .
```

The test suite is the required local verification path. This repository intentionally has no GitHub Actions workflow.

## Adding a tool

1. Put deterministic logic in `tools/`.
2. Validate all required inputs at the tool boundary.
3. Return structured success and error dictionaries.
4. Add focused unit tests for valid, invalid, and failure inputs.
5. Register the tool only with the agents that need it.
6. Update `SYSTEM_DESIGN.md` if the data flow changes.

## Adding an agent

1. Create the smallest specialist agent that owns the new responsibility.
2. Give it a narrow instruction and explicit tool list.
3. Register it with the root agent or nearest orchestrator.
4. Add configuration and trace tests.
5. Document delegation and failure behavior.

## Configuration rules

- Keep secrets in `.env`; never commit them.
- Use `WEATHER_PROVIDER=demo` for deterministic offline tests.
- Use `WEATHER_PROVIDER=open_meteo` only when network access is intended.
- Do not add real booking or payment credentials to this learning project.

## Release readiness

Before treating a change as complete, confirm that tests pass, docs match the code, no secrets or generated files are tracked, and demo-only boundaries remain visible to users.
