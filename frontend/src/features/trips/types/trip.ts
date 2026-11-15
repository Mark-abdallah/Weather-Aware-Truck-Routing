export type LevelName = 'low' | 'moderate' | 'high' | 'severe' | 'no_travel'

export type Cause = 'wind' | 'rain' | 'snow'

export type IntervalMiles = 10 | 25 | 50

export interface Place {
  label: string
  lat: number
  lon: number
}

export interface TripInput {
  origin: Place
  destination: Place
  departure: string
  gross_weight_lb: number
  interval_mi: IntervalMiles
}

export interface Checkpoint {
  lat: number
  lon: number
  mile: number
  eta_utc: string
  wind_mph: number
  gust_mph: number
  rain_in_hr: number
  snow_in_hr: number
  level: number
  level_name: LevelName
  causes: Cause[]
  load_rule_applied: boolean
}

export interface RouteMetrics {
  total_miles: number
  average_risk: number
  miles_by_level: Partial<Record<LevelName, number>>
}

export interface Route {
  route_id: string
  rank: number
  recommended: boolean
  has_no_travel: boolean
  length_miles: number
  duration_s: number
  polyline: [number, number][]
  metrics: RouteMetrics
  checkpoints: Checkpoint[]
}

export interface Heatmap {
  points: [number, number][]
  hours: string[]
  levels: number[][]
}

export interface Trip {
  computed_at: string
  inputs: TripInput
  plan: { notice: string | null; routes: Route[] }
  heatmap: Heatmap
}
