import type { Map as MapLibreMap } from 'maplibre-gl'
import { useEffect, useRef, type RefObject } from 'react'
import { heatmapCollection } from '../map/heatmapGeoJson'
import {
  bindTripLayers,
  createTripMap,
  setHeatmapData,
} from '../map/tripLayers'
import type { Heatmap, Route } from '../types/trip'

interface MapSetup {
  routes: Route[]
  heatmap: Heatmap
  hourRef: RefObject<number>
}

/** Owns the MapLibre map; the heatmap hour switches client-side without re-creating it. */
export function useTripMap(
  routes: Route[],
  heatmap: Heatmap,
  hourIndex: number,
) {
  const hourRef = useRef(hourIndex)
  const { containerRef, mapRef } = useMapInstance({ routes, heatmap, hourRef })
  useEffect(() => {
    hourRef.current = hourIndex
    if (mapRef.current)
      setHeatmapData(mapRef.current, heatmapCollection(heatmap, hourIndex))
  }, [heatmap, hourIndex, mapRef])
  return containerRef
}

/** Creates the map once per routes/heatmap pair (refs are stable, so no other re-creation). */
function useMapInstance({ routes, heatmap, hourRef }: MapSetup) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  useEffect(
    () => mountMap(containerRef.current, mapRef, { routes, heatmap, hourRef }),
    [routes, heatmap, hourRef],
  )
  return { containerRef, mapRef }
}

function mountMap(
  container: HTMLDivElement | null,
  mapRef: RefObject<MapLibreMap | null>,
  { routes, heatmap, hourRef }: MapSetup,
): (() => void) | undefined {
  if (!container) return undefined
  const map = createTripMap(container, routes)
  bindTripLayers(map, routes, () => heatmapCollection(heatmap, hourRef.current))
  mapRef.current = map
  return () => {
    map.remove()
    mapRef.current = null
  }
}
