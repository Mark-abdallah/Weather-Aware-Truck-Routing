import 'maplibre-gl/dist/maplibre-gl.css'
import { useTripMap } from '../hooks/useTripMap'
import type { Route } from '../types/trip'

export function TripMap({ routes }: { routes: Route[] }) {
  const containerRef = useTripMap(routes)
  return (
    <div
      ref={containerRef}
      className="trip-map"
      aria-label="Route map"
      role="region"
    />
  )
}
