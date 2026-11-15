import type { Checkpoint, Route, Trip } from '../features/trips/types/trip'

const BASE_CHECKPOINT: Checkpoint = {
  lat: 40,
  lon: -100,
  mile: 25,
  eta_utc: '2026-01-01T12:00:00+00:00',
  wind_mph: 30,
  gust_mph: 41.4,
  rain_in_hr: 0.1,
  snow_in_hr: 0,
  level: 1,
  level_name: 'moderate',
  causes: ['wind', 'rain'],
  load_rule_applied: false,
}

const BASE_ROUTE: Route = {
  route_id: 'r1',
  rank: 1,
  recommended: true,
  has_no_travel: false,
  length_miles: 100.4,
  duration_s: 5400,
  polyline: [
    [40, -100],
    [41, -99],
  ],
  metrics: {
    total_miles: 100,
    average_risk: 0.5,
    miles_by_level: { low: 50, moderate: 50 },
  },
  checkpoints: [BASE_CHECKPOINT],
}

const BASE_TRIP: Trip = {
  id: 'trip-1',
  computed_at: '2026-01-01T10:00:00+00:00',
  inputs: {
    origin: { label: 'Denver', lat: 40, lon: -100 },
    destination: { label: 'Kansas City', lat: 41, lon: -99 },
    departure: '2026-01-01T11:00:00Z',
    gross_weight_lb: 30000,
    interval_mi: 25,
  },
  plan: { notice: null, routes: [BASE_ROUTE] },
  heatmap: {
    points: [[40, -100]],
    hours: ['2026-01-01T11:00:00+00:00'],
    levels: [[0]],
  },
}

export function makeCheckpoint(
  overrides: Partial<Checkpoint> = {},
): Checkpoint {
  return { ...BASE_CHECKPOINT, ...overrides }
}

export function makeRoute(overrides: Partial<Route> = {}): Route {
  return { ...BASE_ROUTE, ...overrides }
}

export function makeTrip(overrides: Partial<Trip> = {}): Trip {
  return { ...BASE_TRIP, ...overrides }
}
