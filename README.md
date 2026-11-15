# Spotter — Weather-Aware Truck Routing

Helps a truck driver pick the safest of up to three HERE truck routes, based on the forecast
weather along each route at the time the truck will actually be there, the load weight, and travel time.

The product spec, with every confirmed decision, is in [`docs/SPEC.md`](docs/SPEC.md).

## Features

- Origin/destination autosuggest (HERE, proxied through Django so the key stays server-side).
- Up to 3 truck routes (HERE Routing v8, gross weight sent in kg); a notice when fewer come back.
- Checkpoints every 10 / 25 / 50 miles plus the destination, each with an ETA interpolated from
  HERE span durations and the Open-Meteo forecast hour nearest that ETA.
- Risk per checkpoint (Low → No Travel) from sustained wind, rain and snow, with load rules
  applied to wind; all tied causes are kept.
- Distance-weighted route metrics and a ranking: No Travel miles → Severe miles → High miles →
  average risk → travel time. Routes with No Travel miles are still shown, with a warning.
- MapLibre map (OpenFreeMap tiles): routes, the recommended route highlighted, risk-coloured
  checkpoints with popups, and a corridor heatmap with a 0–48 h slider that switches hours on the client.
- Every trip is stored and shareable at `/trips/<uuid>` as a snapshot with its "computed at" time.

## Architecture

```
frontend/ (React + TypeScript + Vite)          backend/ (Django + DRF)
  src/features/trips/                            trips/
    api/        HTTP calls                         domain/        pure rules: risk, load rules, metrics,
    hooks/      TanStack Query + form/map logic                   ranking, checkpoints, forecast hour, grid
    components/ rendering only                     services/      use cases: TripPlanner, HeatmapService,
    map/        GeoJSON + MapLibre layers                         TripService; ports (Protocols)
  src/shared/   http client, Field, formatting     clients/       HERE routing/autosuggest, Open-Meteo,
                                                                  flexible-polyline decoder, cached fetcher
                                                   repositories/  the only ORM code (trips, response cache)
                                                   api/           serializers, thin views, error mapping,
                                                                  composition root (dependencies.py)
```

- **Dependency direction**: `api → services → domain`; `clients` and `repositories` implement the
  service ports and are wired in `trips/api/dependencies.py`, so services are tested with fakes.
- **Request flow** (`POST /api/trips`): validate → fetch routes → sample checkpoints → one batched
  weather fetch (retried once) → assess and rank → build the 49-hour heatmap → store → `201`.
- **Caching**: provider responses are stored in Postgres (`CachedResponse`), keyed by a hash of the
  exact request (API key excluded): weather 1 h, routes and suggestions 24 h. Only responses that
  parse are cached; expired rows are purged lazily on read.

### API

| Method | Path | Result |
|---|---|---|
| `POST` | `/api/trips` | `201 {id, computed_at, inputs, plan, heatmap}` |
| `GET` | `/api/trips/<uuid>` | stored trip, or `404` |
| `GET` | `/api/autosuggest?q=` | `[{label, lat, lon}]` |
| `GET` | `/api/health` | `{"status": "ok"}` |

Errors: `400` invalid input (field messages), `422` no route found, `502` provider unavailable
(e.g. "Weather service unavailable, try again"). A route is never returned without weather.

## Key decisions

- Weight is **gross vehicle weight** in lb, `0 < w ≤ 80,000`.
- Departure must be from 1 hour ago to 7 days ahead; the browser sends ISO with offset, the backend
  works in UTC, and times are shown in the browser's time zone.
- Risk thresholds use an inclusive lower bound at every edge; Open-Meteo snowfall (cm) and rain (mm)
  are converted to in/hr; gusts are informational only.
- Heatmap: ~15 mi grid within 30 mi of any route, capped at ~600 points, load-aware, hour *h* =
  departure + *h* at every point.
- You must pick an autosuggest result (it carries coordinates); there is no free-text geocoding.

## Local setup

Requirements: Python 3.13, Node 22+, PostgreSQL (SQLite is used automatically if `DATABASE_URL` is unset).

```bash
cp .env.example .env            # set HERE_API_KEY (and DATABASE_URL for Postgres)

cd backend
python -m venv .venv && .venv/Scripts/activate   # macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py runserver      # http://localhost:8000

cd ../frontend
npm install
npm run dev                     # http://localhost:5173 (VITE_API_URL defaults to http://localhost:8000)
```

## Tests and checks

```bash
cd backend  && pytest && ruff check . && python manage.py makemigrations --check
cd frontend && npm test && npm run lint && npm run build
```

## Deployment (Render)

`render.yaml` is a Blueprint for a free Postgres database, the Django API (gunicorn, migrations at
start) and the React static site with an SPA rewrite. After the first deploy, set `HERE_API_KEY` and
`CORS_ALLOWED_ORIGINS` on `spotter-api`, and `VITE_API_URL` on `spotter-web` (then redeploy the site).

## Out of scope

Authentication, multiple stops, a custom routing engine, live traffic re-routing, notifications, mobile app.
