import {
  FullscreenControl,
  Map as MapLibreMap,
  NavigationControl,
  Popup,
  ScaleControl,
  type ExpressionSpecification,
  type GeoJSONSource,
  type MapLayerMouseEvent,
  type PaddingOptions,
} from 'maplibre-gl'
import type { FeatureCollection } from 'geojson'
import type { Route, Trip } from '../types/trip'
import { checkpointPopupContent } from './checkpointPopup'
import { heatmapCollection } from './heatmapGeoJson'
import {
  BRAND,
  CHECKPOINT_LAYER,
  LAYER_ORDER,
  ROUTE_CASING_LAYER,
  ROUTE_LINE_LAYER,
  SOURCES,
} from './mapLayers'
import {
  checkpointsCollection,
  endpointsCollection,
  routeBounds,
  routesCollection,
} from './tripGeoJson'

export const MAP_STYLE_URL = 'https://tiles.openfreemap.org/styles/liberty'
const FIT_DURATION_MS = 700
const COMPACT_WIDTH_PX = 720
const COMPACT_PADDING_PX = 32
const WIDE_PADDING: PaddingOptions = {
  top: 64,
  right: 72,
  bottom: 200,
  left: 64,
}
const POPUP_OPTIONS = { maxWidth: '300px', className: 'checkpoint-popup' }
const MAP_ATTRIBUTION = { compact: true }
const SELECTED_STYLE = { color: BRAND.teal, width: 7, casing: 13, sortKey: 1 }
const OTHER_STYLE = { color: BRAND.muted, width: 4, casing: 8, sortKey: 0 }

export interface MapView {
  hourIndex: number
  selectedId: string
  onSelectRoute: (routeId: string) => void
}

export function createTripMap(
  container: HTMLElement,
  routes: Route[],
): MapLibreMap {
  const bounds = routeBounds(routes)
  const options = { container, style: MAP_STYLE_URL, bounds }
  const map = new MapLibreMap({
    ...options,
    attributionControl: MAP_ATTRIBUTION,
  })
  map.addControl(new NavigationControl({ visualizePitch: false }), 'top-right')
  map.addControl(new FullscreenControl(), 'top-right')
  map.addControl(new ScaleControl({ unit: 'imperial' }), 'top-left')
  return map
}

export function bindTripLayers(
  map: MapLibreMap,
  trip: Trip,
  currentView: () => MapView,
): void {
  const routes = trip.plan.routes
  map.on('load', () => addTripLayers(map, trip, currentView()))
  map.on('click', CHECKPOINT_LAYER.id, (event) =>
    showCheckpointPopup(map, event, routes),
  )
  map.on('click', ROUTE_CASING_LAYER.id, (event) =>
    selectClickedRoute(event, currentView()),
  )
  showPointerOver(map, [CHECKPOINT_LAYER.id, ROUTE_CASING_LAYER.id])
}

function addTripLayers(map: MapLibreMap, trip: Trip, view: MapView): void {
  const routes = trip.plan.routes
  const heatmap = heatmapCollection(trip.heatmap, view.hourIndex)
  addGeoJson(map, SOURCES.heatmap, heatmap)
  addGeoJson(map, SOURCES.routes, routesCollection(routes))
  addGeoJson(map, SOURCES.checkpoints, checkpointsCollection(routes))
  addGeoJson(map, SOURCES.endpoints, endpointsCollection(trip.inputs))
  for (const layer of LAYER_ORDER) map.addLayer(layer)
  applySelection(map, routes, view.selectedId)
}

function addGeoJson(
  map: MapLibreMap,
  id: string,
  data: FeatureCollection,
): void {
  map.addSource(id, { type: 'geojson', data })
}

export function setHeatmapData(
  map: MapLibreMap,
  data: FeatureCollection,
): void {
  map.getSource<GeoJSONSource>(SOURCES.heatmap)?.setData(data)
}

export function applySelection(
  map: MapLibreMap,
  routes: Route[],
  selectedId: string,
): void {
  if (!map.getLayer(ROUTE_LINE_LAYER.id)) return
  styleRoutes(map, selectionPicker(selectedId))
  map.setFilter(CHECKPOINT_LAYER.id, ['==', ['get', 'route_id'], selectedId])
  fitRoute(
    map,
    routes.find((route) => route.route_id === selectedId),
  )
}

type Pick = (key: keyof typeof SELECTED_STYLE) => ExpressionSpecification

function styleRoutes(map: MapLibreMap, pick: Pick): void {
  map.setPaintProperty(ROUTE_LINE_LAYER.id, 'line-color', pick('color'))
  map.setPaintProperty(ROUTE_LINE_LAYER.id, 'line-width', pick('width'))
  map.setPaintProperty(ROUTE_CASING_LAYER.id, 'line-width', pick('casing'))
  for (const id of [ROUTE_CASING_LAYER.id, ROUTE_LINE_LAYER.id])
    map.setLayoutProperty(id, 'line-sort-key', pick('sortKey'))
}

function selectionPicker(selectedId: string): Pick {
  const isSelected: ExpressionSpecification = [
    '==',
    ['get', 'route_id'],
    selectedId,
  ]
  return (key) => ['case', isSelected, SELECTED_STYLE[key], OTHER_STYLE[key]]
}

function fitRoute(map: MapLibreMap, route: Route | undefined): void {
  if (!route) return
  const compact = map.getContainer().clientWidth < COMPACT_WIDTH_PX
  const padding = compact ? COMPACT_PADDING_PX : WIDE_PADDING
  map.fitBounds(routeBounds([route]), { padding, duration: FIT_DURATION_MS })
}

function selectClickedRoute(event: MapLayerMouseEvent, view: MapView): void {
  const routeId = event.features?.[0]?.properties?.route_id
  if (typeof routeId === 'string' && routeId !== view.selectedId)
    view.onSelectRoute(routeId)
}

function showPointerOver(map: MapLibreMap, layerIds: string[]): void {
  for (const id of layerIds) {
    map.on('mouseenter', id, () => (map.getCanvas().style.cursor = 'pointer'))
    map.on('mouseleave', id, () => (map.getCanvas().style.cursor = ''))
  }
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
  new Popup(POPUP_OPTIONS)
    .setLngLat([checkpoint.lon, checkpoint.lat])
    .setDOMContent(checkpointPopupContent(checkpoint))
    .addTo(map)
}
