import { expect, it } from 'vitest'
import { makeCheckpoint, makeRoute } from '../../../test/tripFixture'
import { LEVEL_COLORS } from '../risk'
import {
  checkpointsCollection,
  routeBounds,
  routesCollection,
} from './tripGeoJson'

const ROUTES = [
  makeRoute({ route_id: 'a', recommended: true }),
  makeRoute({
    route_id: 'b',
    recommended: false,
    polyline: [
      [39, -101],
      [42, -98],
    ],
    checkpoints: [
      makeCheckpoint(),
      makeCheckpoint({ level_name: 'no_travel' }),
    ],
  }),
]

it('builds route lines in [lon, lat] order with the recommended flag', () => {
  const [first, second] = routesCollection(ROUTES).features
  expect(first.geometry).toEqual({
    type: 'LineString',
    coordinates: [
      [-100, 40],
      [-99, 41],
    ],
  })
  expect(first.properties).toEqual({ route_id: 'a', recommended: true })
  expect(second.properties?.recommended).toBe(false)
})

it('builds checkpoints coloured by level with indexes back to the data', () => {
  const features = checkpointsCollection(ROUTES).features
  expect(features).toHaveLength(3)
  expect(features[2].properties).toEqual({
    routeIndex: 1,
    checkpointIndex: 1,
    color: LEVEL_COLORS.no_travel,
  })
  expect(features[0].geometry).toEqual({
    type: 'Point',
    coordinates: [-100, 40],
  })
})

it('bounds cover every route point', () => {
  expect(routeBounds(ROUTES)).toEqual([
    [-101, 39],
    [-98, 42],
  ])
})
