# Task plan (one commit each)

Backend app: `backend/trips` with `domain/` (pure), `services/`, `repositories/`, `clients/`, `api/`.
Python: `C:\Users\mark.elgendy\AppData\Local\Programs\Python\Python313\python.exe` → venv at `backend/.venv`.
PostgreSQL not installed yet: DB tests marked `django_db`; non-DB tests must pass without PG.

1. [ ] Backend scaffolding — Django `config` + app `trips`, DRF, env-based settings (dj-database-url, SECRET_KEY, DEBUG, ALLOWED_HOSTS, HERE_API_KEY, CORS), `/api/health`, pytest + ruff config.
2. [ ] Frontend scaffolding — Vite React TS, ESLint, Prettier, Vitest + RTL, TanStack Query, `src/features`, `src/shared`, `VITE_API_URL`.
3. [x] Git init + .gitignore
4. [ ] Domain: RiskLevel + wind/rain/snow classification (edge tests)
5. [ ] Domain: load rules + checkpoint assessment (worst level + all tied causes)
6. [ ] Domain: distance-weighted route metrics
7. [ ] Domain: recommendation ranking (no_travel, severe, high, avg, duration)
8. [ ] Domain: geometry + checkpoint sampling + ETA interpolation
9. [ ] Domain: nearest forecast hour + heatmap corridor grid (15 mi, 30 mi buffer, ~600 cap)
10. [ ] Services: trip planner + heatmap service with injected ports (fakes in tests)
11. [ ] Clients: HERE (routing/geocode/autosuggest, flexible polyline) + Open-Meteo (batched, retry once) + DB cache
12. [ ] Trip model + API (POST/GET trips, autosuggest proxy, validation, error mapping)
13. [ ] Frontend: API layer, types, trip form
14. [ ] Frontend: routing, trip page, MapLibre map (routes + checkpoints + popups)
15. [ ] Frontend: route summary cards
16. [ ] Frontend: heatmap layer + 0–48 h slider (client-side switching)
17. [ ] render.yaml + README
