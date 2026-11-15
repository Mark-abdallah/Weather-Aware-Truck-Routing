import type {
  CircleLayerSpecification,
  ExpressionSpecification,
  LineLayerSpecification,
  SymbolLayerSpecification,
} from 'maplibre-gl'

export const SOURCES = {
  heatmap: 'heatmap',
  routes: 'routes',
  checkpoints: 'checkpoints',
  endpoints: 'endpoints',
} as const

export const BRAND = {
  ink: '#043b4b',
  teal: '#008080',
  coral: '#f84960',
  mist: '#bcddde',
  muted: '#7f98a0',
  white: '#ffffff',
}

const LABEL_FONT = ['Noto Sans Bold']
const ORIGIN_OR_DESTINATION: ExpressionSpecification = [
  'case',
  ['==', ['get', 'kind'], 'origin'],
  BRAND.teal,
  BRAND.coral,
]

export const HEATMAP_LAYER: CircleLayerSpecification = {
  id: 'heatmap',
  type: 'circle',
  source: SOURCES.heatmap,
  paint: {
    'circle-color': ['get', 'color'],
    'circle-opacity': 0.28,
    'circle-blur': 0.45,
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, 5, 7, 14, 10, 30],
  },
}

export const ROUTE_CASING_LAYER: LineLayerSpecification = {
  id: 'route-casing',
  type: 'line',
  source: SOURCES.routes,
  layout: { 'line-cap': 'round', 'line-join': 'round' },
  paint: { 'line-color': BRAND.white, 'line-width': 8 },
}

export const ROUTE_LINE_LAYER: LineLayerSpecification = {
  id: 'route-line',
  type: 'line',
  source: SOURCES.routes,
  layout: { 'line-cap': 'round', 'line-join': 'round' },
  paint: { 'line-color': BRAND.muted, 'line-width': 4 },
}

export const ROUTE_LABEL_LAYER: SymbolLayerSpecification = {
  id: 'route-label',
  type: 'symbol',
  source: SOURCES.routes,
  layout: {
    'symbol-placement': 'line',
    'text-field': ['get', 'label'],
    'text-font': LABEL_FONT,
    'text-size': 12,
    'symbol-spacing': 320,
  },
  paint: {
    'text-color': BRAND.ink,
    'text-halo-color': BRAND.white,
    'text-halo-width': 2,
  },
}

export const CHECKPOINT_LAYER: CircleLayerSpecification = {
  id: 'checkpoints',
  type: 'circle',
  source: SOURCES.checkpoints,
  paint: {
    'circle-color': ['get', 'color'],
    'circle-radius': ['interpolate', ['linear'], ['zoom'], 4, 4.5, 9, 8],
    'circle-stroke-color': BRAND.white,
    'circle-stroke-width': 2.5,
  },
}

export const ENDPOINT_LAYER: CircleLayerSpecification = {
  id: 'endpoints',
  type: 'circle',
  source: SOURCES.endpoints,
  paint: {
    'circle-color': ORIGIN_OR_DESTINATION,
    'circle-radius': 9,
    'circle-stroke-color': BRAND.white,
    'circle-stroke-width': 3,
  },
}

export const ENDPOINT_LABEL_LAYER: SymbolLayerSpecification = {
  id: 'endpoint-label',
  type: 'symbol',
  source: SOURCES.endpoints,
  layout: {
    'text-field': ['get', 'label'],
    'text-font': LABEL_FONT,
    'text-size': 13,
    'text-offset': [0, 1.4],
    'text-anchor': 'top',
    'text-allow-overlap': true,
  },
  paint: {
    'text-color': BRAND.ink,
    'text-halo-color': BRAND.white,
    'text-halo-width': 2.5,
  },
}

export const LAYER_ORDER = [
  HEATMAP_LAYER,
  ROUTE_CASING_LAYER,
  ROUTE_LINE_LAYER,
  ROUTE_LABEL_LAYER,
  CHECKPOINT_LAYER,
  ENDPOINT_LAYER,
  ENDPOINT_LABEL_LAYER,
]
