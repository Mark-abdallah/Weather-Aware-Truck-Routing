# Weather-Aware Truck Routing — Spec

Source brief: `fs-assessment-spotter.pdf`. Decisions below were confirmed with the user and are binding.

## Goal
React + Django app that helps a truck driver choose the safest route based on weather, load weight, and travel time.

## Inputs
- Origin & destination (geocoded via HERE Geocoding/Autosuggest)
- Departure date/time (must be within the forecast window)
- Load weight (lb)
- Sampling interval: user selects **10 / 25 / 50 miles** (default 25)

## External services
| Purpose | Service |
|---|---|
| Routing (truck, 3 alternatives) | **HERE Routing v8**, `transportMode=truck`, pass gross weight, `alternatives=2` → 3 routes |
| Geocoding | HERE Geocoding & Search |
| Weather | **Open-Meteo** hourly forecast (no key), batch multi-location requests |
| Map | **MapLibre GL** with free vector tiles |
| Hosting | **Render** (`render.yaml`: Django web service and React static site; no database) |

If HERE returns fewer than 3 routes, show what was returned and tell the user.

## Checkpoints
- Place one every N miles along each route polyline, plus the destination.
- ETA at a checkpoint = departure + travel time to that point (from HERE section/span durations, interpolated along the polyline).
- Weather is taken from the forecast hour closest to the ETA.

## Risk classification (per checkpoint)
Levels, scored: Low=0, Moderate=1, High=2, Severe=3, No Travel=4.
**Lower bound inclusive** at every edge.

| Condition | Low | Moderate | High | Severe | No Travel |
|---|---|---|---|---|---|
| Wind (sustained 10 m, mph) | <25 | 25–<35 | 35–<45 | 45–<55 | ≥55 |
| Rain (in/hr) | <0.10 | 0.10–<0.25 | 0.25–<0.50 | 0.50–≤1.00 | >1.00 |
| Snow (in/hr) | <0.5 | 0.5–<1.0 | 1.0–<2.0 | 2.0–≤3.0 | >3.0 |

- Wind = **sustained** wind speed; gusts shown for information only.
- Open-Meteo snowfall is in cm/hr; convert to in/hr.

Load rules (applied to the wind level):
- ≥55 mph → No Travel (any load)
- 45–<55 mph and load >30,000 lb → No Travel
- 35–<45 mph and load >40,000 lb → Severe

**Overall checkpoint level = worst of wind (after load rules), rain, snow.** Record which condition caused it.

## Route metrics (distance-weighted)
- Each checkpoint covers the road segment from the previous checkpoint (or origin) up to it.
- Miles per level = sum of segment lengths at that level.
- Average risk = Σ(level score × segment miles) / total miles.

## Recommendation (sort ascending, first wins)
1. No Travel miles
2. Severe miles
3. High miles
4. Average risk
5. Travel time

Routes with any No Travel miles are still shown, with a clear warning.

## UI
- Form: origin, destination (autosuggest), departure, load weight, interval.
- Map: all routes (recommended route highlighted), checkpoints coloured by risk, popups with ETA, conditions, level and cause.
- Route summary cards: distance, duration, miles per level, average risk, recommended badge, No Travel warning.
- **Heatmap**: a grid of points covering the corridor around all routes, coloured by combined risk level, with a **0–48 h slider** (hourly steps from departure). Fetch all 49 hours at once and switch hours on the client only, so the slider stays smooth.

## Persistence
- None. The app is stateless: `POST /api/trips` computes and returns the plan; nothing is stored and there are no shareable trip links.
- HERE and Open-Meteo responses are cached in memory per server process, with an expiry time (weather about 1 h, routes about 24 h).

## Additional confirmed decisions
- **Weight** = gross vehicle weight in lb, labelled "Gross weight (lb)", must be >0 and ≤80,000. Sent to HERE converted to kg.
- **Departure**: from now−1h to now+7 days. Browser sends ISO with offset; backend works in UTC; ETAs displayed in browser time zone.
- **Weather failure**: retry once; if still failing → 502 "Weather service unavailable, try again". Never show a route without weather data.
- **Heatmap**: grid ~15 mi spacing, points within 30 mi of any route, cap ~600 points; load-aware (same classifier as checkpoints); hour h = departure + h at every point.
- **Cause tie-break**: store all tied causes; show them all in the popup.
- **Tiles**: OpenFreeMap (no key). HERE key stays server-side; autosuggest proxied through Django.
- **Cache**: expired entries purged on read.

## Out of scope
Auth/users, multiple stops, a self-built routing engine, real-time traffic re-routing, notifications, mobile app.

## Deliverables
GitHub repo, hosted app on Render, README (setup, architecture, decisions), 5–10 min Loom (done by the user).
