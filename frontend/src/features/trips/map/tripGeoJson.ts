import type { Feature, FeatureCollection } from 'geojson'
import type { Checkpoint, Route } from '../types/trip'
import { LEVEL_COLORS } from '../risk'

/** Backend points are [lat, lon]; GeoJSON and MapLibre use [lon, lat]. */
export type LonLat = [number, number]

export function toLonLat([lat, lon]: [number, number]): LonLat {
  return [lon, lat]
}

export function routesCollection(routes: Route[]): FeatureCollection {
  return { type: 'FeatureCollection', features: routes.map(routeFeature) }
}

function routeFeature(route: Route): Feature {
  const geometry = {
    type: 'LineString' as const,
    coordinates: route.polyline.map(toLonLat),
  }
  const properties = {
    route_id: route.route_id,
    recommended: route.recommended,
  }
  return { type: 'Feature', geometry, properties }
}

export function checkpointsCollection(routes: Route[]): FeatureCollection {
  const features = routes.flatMap((route, routeIndex) =>
    route.checkpoints.map((checkpoint, checkpointIndex) =>
      checkpointFeature(checkpoint, [routeIndex, checkpointIndex]),
    ),
  )
  return { type: 'FeatureCollection', features }
}

function checkpointFeature(
  checkpoint: Checkpoint,
  [routeIndex, checkpointIndex]: [number, number],
): Feature {
  const geometry = {
    type: 'Point' as const,
    coordinates: [checkpoint.lon, checkpoint.lat],
  }
  const color = LEVEL_COLORS[checkpoint.level_name]
  return {
    type: 'Feature',
    geometry,
    properties: { routeIndex, checkpointIndex, color },
  }
}

/** [[west, south], [east, north]] covering every route point (a loop: polylines can be huge). */
export function routeBounds(routes: Route[]): [LonLat, LonLat] {
  let [west, south, east, north] = [Infinity, Infinity, -Infinity, -Infinity]
  for (const [lat, lon] of routes.flatMap((route) => route.polyline)) {
    ;[west, east] = [Math.min(west, lon), Math.max(east, lon)]
    ;[south, north] = [Math.min(south, lat), Math.max(north, lat)]
  }
  return [
    [west, south],
    [east, north],
  ]
}
