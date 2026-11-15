# Spotter

**Product spec: `docs/SPEC.md` — read it before any task. Its decisions are confirmed by the user; don't change them without asking.**
API keys (`HERE_API_KEY`, `DATABASE_URL`) come from env vars / `.env` (never committed).

## Stack (always use the latest stable versions)
- **Backend**: Python + Django + Django REST Framework, in `backend/`
- **Frontend**: React + TypeScript + Vite, in `frontend/`
- **Database**: PostgreSQL (via `psycopg` 3); settings from environment variables, never hard-coded

## Backend architecture (Django)
- One Django app per bounded domain (e.g. `users`, `orders`).
- Layers inside each app:
  - `domain/` — entities, value objects, business rules. Pure Python, no Django imports.
  - `services/` — use cases; orchestrate domain + repositories.
  - `repositories/` — the only place that touches the ORM (`models.py`).
  - `api/` — DRF serializers, views, urls. Views are thin: validate → call service → return response.
- Dependencies are injected (pass repositories into services), so services are testable without the DB.
- Migrations committed with each model change. Tests with `pytest` + `pytest-django`.
- Lint/format: `ruff`. Type hints everywhere.

## Frontend architecture (React)
- Feature-based folders: `src/features/<feature>/{components,hooks,api,types}`; shared code in `src/shared/`.
- Function components + hooks only. Components handle rendering; logic goes in custom hooks; HTTP goes in `api/` modules.
- Server state with TanStack Query; no business logic in components.
- Tests with Vitest + React Testing Library. Lint with ESLint, format with Prettier.

## Priorities
**Correctness and clarity over extra features.** Build only what the requirement asks for. No speculative features, options, or abstractions "for later". When unsure, choose the simpler, more obviously correct solution. A smaller feature that works and is tested beats a larger one that might not.

**Ask, don't assume.** When any part of a feature is unclear, interview the user before implementing it.

## Code rules (all code)
- SOLID and clean architecture.
- **No function, method or component body longer than 10 lines.**
- Max 3 parameters, clear names, no magic numbers, no duplication.

## Commands
- Backend: `cd backend && pytest`, `ruff check .`, `python manage.py makemigrations --check`
- Frontend: `cd frontend && npm test`, `npm run lint`, `npm run build`
