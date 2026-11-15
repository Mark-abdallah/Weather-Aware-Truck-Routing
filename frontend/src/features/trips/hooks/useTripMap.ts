import { useEffect, useRef } from 'react'
import { bindTripLayers, createTripMap } from '../map/tripLayers'
import type { Route } from '../types/trip'

/** Owns the MapLibre map for a set of routes; returns the container ref. */
export function useTripMap(routes: Route[]) {
  const containerRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!containerRef.current) return
    const map = createTripMap(containerRef.current, routes)
    bindTripLayers(map, routes)
    return () => map.remove()
  }, [routes])
  return containerRef
}
