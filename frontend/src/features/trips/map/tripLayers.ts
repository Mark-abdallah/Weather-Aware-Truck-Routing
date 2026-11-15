import {
  Map as MapLibreMap,
  Popup,
  type CircleLayerSpecification,
  type ExpressionSpecification,
  type LineLayerSpecification,
  type MapLayerMouseEvent,
} from 'maplibre-gl'
import type { Route } from '../types/trip'
import { checkpointPopupContent } from './checkpointPopup'
import {
  checkpointsCollection,
  routeBounds,
  routesCollection,
} from './tripGeoJson'

export const MAP_STYLE_URL = 'https://tiles.openfreemap.org/styles/liberty'
const ROUTE_SOURCE = 'routes'
const CHECKPOINT_SOURCE = 'checkpoints'
const FIT_PADDING_PX = 48
const IS_RECOMMENDED: ExpressionSpecification = ['get', 'recommended']

const ROUTE_LAYER: LineLayerSpecification = {
  id: 'routes',
  type: 'line',
  source: ROUTE_SOURCE,
  layout: {
    'line-cap': 'round',
    'line-sort-key': ['case', IS_RECOMMENDED, 1, 0],
  },
  paint: {
    'line-color': ['case', IS_RECOMMENDED, '#2563eb', '#6b7280'],
    'line-width': ['case', IS_RECOMMENDED, 6, 4],
  },
}

const CHECKPOINT_LAYER: CircleLayerSpecification = {
  id: 'checkpoints',
  type: 'circle',
  source: CHECKPOINT_SOURCE,
  paint: {
    'circle-color': ['get', 'color'],
    'circle-radius': 6,
    'circle-stroke-color': '#ffffff',
    'circle-stroke-width': 2,
  },
}

export function createTripMap(
  container: HTMLElement,
  routes: Route[],
): MapLibreMap {
  const fitBoundsOptions = { padding: FIT_PADDING_PX }
  const bounds = routeBounds(routes)
  return new MapLibreMap({
    container,
    style: MAP_STYLE_URL,
    bounds,
    fitBoundsOptions,
  })
}

/** Adds the route and checkpoint layers once the style loads, plus checkpoint popups. */
export function bindTripLayers(map: MapLibreMap, routes: Route[]): void {
  map.on('load', () => addTripLayers(map, routes))
  map.on('click', CHECKPOINT_LAYER.id, (event) =>
    showCheckpointPopup(map, event, routes),
  )
}

function addTripLayers(map: MapLibreMap, routes: Route[]): void {
  map.addSource(ROUTE_SOURCE, {
    type: 'geojson',
    data: routesCollection(routes),
  })
  map.addSource(CHECKPOINT_SOURCE, {
    type: 'geojson',
    data: checkpointsCollection(routes),
  })
  map.addLayer(ROUTE_LAYER)
  map.addLayer(CHECKPOINT_LAYER)
}

function showCheckpointPopup(
  map: MapLibreMap,
  event: MapLayerMouseEvent,
  routes: Route[],
): void {
  const properties = event.features?.[0]?.properties
  const route = properties ? routes[properties.routeIndex] : undefined
  const checkpoint = route?.checkpoints[properties?.checkpointIndex]
  if (!checkpoint) return
  const content = checkpointPopupContent(checkpoint)
  new Popup()
    .setLngLat([checkpoint.lon, checkpoint.lat])
    .setDOMContent(content)
    .addTo(map)
}
