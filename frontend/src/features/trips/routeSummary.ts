import { LEVEL_LABELS } from './risk'
import type { LevelName, Route } from './types/trip'

const SECONDS_PER_MINUTE = 60
const MINUTES_PER_HOUR = 60
const MILE_DECIMALS = 1
const RISK_DECIMALS = 2
export const LEVEL_ORDER: readonly LevelName[] = [
  'low',
  'moderate',
  'high',
  'severe',
  'no_travel',
]

export interface LevelMiles {
  level: LevelName
  label: string
  miles: string
}

export function formatDuration(seconds: number): string {
  const totalMinutes = Math.round(seconds / SECONDS_PER_MINUTE)
  const hours = Math.floor(totalMinutes / MINUTES_PER_HOUR)
  const minutes = totalMinutes % MINUTES_PER_HOUR
  return hours ? `${hours} h ${minutes} min` : `${minutes} min`
}

export function formatMiles(miles: number): string {
  return `${miles.toFixed(MILE_DECIMALS)} mi`
}

export function formatRisk(averageRisk: number): string {
  return averageRisk.toFixed(RISK_DECIMALS)
}

/** Levels that cover any miles, lowest risk first. */
export function levelBreakdown(route: Route): LevelMiles[] {
  const byLevel = route.metrics.miles_by_level
  return LEVEL_ORDER.filter((level) => (byLevel[level] ?? 0) > 0).map(
    (level) => ({
      level,
      label: LEVEL_LABELS[level],
      miles: formatMiles(byLevel[level] ?? 0),
    }),
  )
}

export function byRank(routes: Route[]): Route[] {
  return [...routes].sort((a, b) => a.rank - b.rank)
}

export interface LevelShare {
  level: LevelName
  percent: number
}

/** Share of the route's miles at each non-zero level, in percent (for the stacked bar). */
export function levelShares(route: Route): LevelShare[] {
  const { total_miles: total, miles_by_level: byLevel } = route.metrics
  if (total <= 0) return []
  const percent = (level: LevelName) => ((byLevel[level] ?? 0) / total) * 100
  return LEVEL_ORDER.filter((level) => percent(level) > 0).map((level) => ({
    level,
    percent: percent(level),
  }))
}
