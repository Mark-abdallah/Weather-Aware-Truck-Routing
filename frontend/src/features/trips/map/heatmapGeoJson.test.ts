import { expect, it } from 'vitest'
import { LEVEL_COLORS } from '../risk'
import { heatmapCollection } from './heatmapGeoJson'

const HEATMAP = {
  points: [
    [40, -100],
    [41, -99],
  ] as [number, number][],
  hours: ['2026-01-01T00:00:00+00:00', '2026-01-01T01:00:00+00:00'],
  levels: [
    [0, 4],
    [2, 3],
  ],
}

it('colours each grid point by its level at the chosen hour', () => {
  const colors = (hour: number) =>
    heatmapCollection(HEATMAP, hour).features.map((f) => f.properties?.color)
  expect(colors(0)).toEqual([LEVEL_COLORS.low, LEVEL_COLORS.no_travel])
  expect(colors(1)).toEqual([LEVEL_COLORS.high, LEVEL_COLORS.severe])
})

it('places points in [lon, lat] order', () => {
  const [first] = heatmapCollection(HEATMAP, 0).features
  expect(first.geometry).toEqual({ type: 'Point', coordinates: [-100, 40] })
})
