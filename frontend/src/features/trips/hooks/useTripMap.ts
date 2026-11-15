import type { Map as MapLibreMap } from 'maplibre-gl'
import { useEffect, useRef, type RefObject } from 'react'
import { heatmapCollection } from '../map/heatmapGeoJson'
import {
  applySelection,
  bindTripLayers,
  createTripMap,
  setHeatmapData,
  type MapView,
} from '../map/tripLayers'
import type { Trip } from '../types/trip'

type ViewRef = RefObject<MapView>
type MapRef = RefObject<MapLibreMap | null>

/** Owns the MapLibre map; hour and selection changes update it without re-creating it. */
export function useTripMap(trip: Trip, view: MapView) {
  const viewRef = useRef(view)
  useEffect(() => {
    viewRef.current = view
  })
  const { containerRef, mapRef } = useMapInstance(trip, viewRef)
  useMapView(mapRef, trip, view)
  return containerRef
}

function useMapView(
  mapRef: MapRef,
  trip: Trip,
  { hourIndex, selectedId }: MapView,
) {
  useEffect(() => {
    if (mapRef.current)
      setHeatmapData(mapRef.current, heatmapCollection(trip.heatmap, hourIndex))
  }, [mapRef, trip.heatmap, hourIndex])
  useEffect(() => {
    if (mapRef.current)
      applySelection(mapRef.current, trip.plan.routes, selectedId)
  }, [mapRef, trip.plan.routes, selectedId])
}

/** Creates the map once per trip (the trip object is stable; refs never change). */
function useMapInstance(trip: Trip, viewRef: ViewRef) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  useEffect(
    () => mountMap(containerRef.current, mapRef, { trip, viewRef }),
    [trip, viewRef],
  )
  return { containerRef, mapRef }
}

function mountMap(
  container: HTMLDivElement | null,
  mapRef: MapRef,
  { trip, viewRef }: { trip: Trip; viewRef: ViewRef },
): (() => void) | undefined {
  if (!container) return undefined
  const map = createTripMap(container, trip.plan.routes)
  bindTripLayers(map, trip, () => viewRef.current)
  mapRef.current = map
  return () => {
    map.remove()
    mapRef.current = null
  }
}
