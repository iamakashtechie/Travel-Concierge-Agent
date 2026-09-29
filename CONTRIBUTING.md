# Contributing

Thank you for improving Travel Concierge. This is a focused learning repository, so changes should remain understandable and easy to run locally.

## Before changing code

- Read [README.md](README.md) for setup and commands.
- Read [SYSTEM_DESIGN.md](SYSTEM_DESIGN.md) for ownership boundaries.
- Check [PLAN.md](PLAN.md) before starting a larger feature.
- Look for an existing test near the code you will change.

## Development standards

- Use Python 3.12 or the project-managed `uv` environment.
- Keep changes focused and preserve existing public names unless a migration is necessary.
- Prefer deterministic tools for validation, persistence, and transformations.
- Keep agent instructions narrow and explicit about when tools should be called.
- Return structured errors from tools; do not hide failures behind fallback text.
- Do not add real booking, payment, or personal data integrations without a documented design change.
- Avoid committing secrets, `.env`, virtual environments, caches, or generated artifacts.

## Tests

Run a focused test while developing, then the complete suite:

```powershell
uv run pytest tests/test_trip_state.py
uv run pytest
```

Add tests for both the normal path and invalid or provider-failure paths. Changes involving routing or orchestration should also update configuration or trace tests.

## Documentation

Update documentation when a change affects setup, commands, architecture, data flow, safety boundaries, or future scope. Keep `README.md` task-oriented and put deeper explanations in the dedicated reference files.

## Pull requests or reviews

There is no automated GitHub Actions workflow in this repository. Before submitting a change for review, include:

- what changed and why
- tests run and their result
- any known limitation or follow-up work
- documentation updated, if applicable
