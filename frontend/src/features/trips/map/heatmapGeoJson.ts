import type { FeatureCollection } from 'geojson'
import { LEVEL_COLORS } from '../risk'
import { LEVEL_ORDER } from '../routeSummary'
import type { Heatmap } from '../types/trip'
import { toLonLat } from './tripGeoJson'

/** Grid points coloured by their risk level at the given hour index. */
export function heatmapCollection(
  heatmap: Heatmap,
  hourIndex: number,
): FeatureCollection {
  const levels = heatmap.levels[hourIndex] ?? []
  const features = heatmap.points.map((point, index) => ({
    type: 'Feature' as const,
    geometry: { type: 'Point' as const, coordinates: toLonLat(point) },
    properties: { color: LEVEL_COLORS[LEVEL_ORDER[levels[index]] ?? 'low'] },
  }))
  return { type: 'FeatureCollection', features }
}
