import type { LevelName } from './types/trip'

export const LEVEL_LABELS: Record<LevelName, string> = {
  low: 'Low',
  moderate: 'Moderate',
  high: 'High',
  severe: 'Severe',
  no_travel: 'No Travel',
}

export const LEVEL_COLORS: Record<LevelName, string> = {
  low: '#16a34a',
  moderate: '#eab308',
  high: '#f97316',
  severe: '#dc2626',
  no_travel: '#7e22ce',
}
