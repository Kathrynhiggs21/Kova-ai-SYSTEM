# Kova AI System Development Instructions

Always follow these instructions first. When the repository already contains a clear convention, prefer it over inventing a new pattern.

## Repository context

This repository contains a Docker-based FastAPI application under `kova-ai/`.

- Primary app entry point: `kova-ai/app/main.py`
- API routers live in `kova-ai/app/api/`
- Database schema lives in `kova-ai/scripts/init.sql`
- Docker and local setup are driven by `setup_kova_system.sh` and `kova-ai/docker-compose.yml`
- Repository verification is handled by `verify_platform.sh`

## Working conventions

- Make minimal, targeted changes. Prefer editing existing files over introducing new abstractions.
- Keep implementation aligned with the existing FastAPI structure and router-based organization.
- Avoid adding new dependencies unless they are clearly required and already justified by the change.
- Do not hardcode secrets or API keys. Use `kova-ai/.env` for local configuration and keep examples in `kova-ai/.env.example`.
- Preserve existing behavior unless the task explicitly requires a change.

## Validation expectations

Before finishing a task, verify the change with the most relevant checks available:

1. Run `./verify_platform.sh` from the repository root.
2. If Python files changed, run `python3 -m py_compile` on the affected files.
3. If the change affects the API surface, verify the relevant endpoint behavior with the local app or Docker setup when possible.
4. If Docker is unavailable, report that clearly and still validate whatever is possible locally.

## Helpful file locations

- `setup_kova_system.sh` — bootstraps or restarts the local environment
- `verify_platform.sh` — lightweight repository validation
- `kova-ai/app/main.py` — FastAPI app registration
- `kova-ai/app/api/` — endpoint routers
- `kova-ai/scripts/init.sql` — database initialization data
- `kova-ai/requirements.txt` — Python dependencies

## Scope guidance

- For API work, update the relevant router file and ensure it is included in `kova-ai/app/main.py`.
- For configuration or environment changes, update `.env.example` when appropriate and keep the change consistent with the existing setup scripts.
- For database changes, update `kova-ai/scripts/init.sql` and verify the schema expectations.
