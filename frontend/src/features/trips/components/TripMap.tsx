import 'maplibre-gl/dist/maplibre-gl.css'
import { useTripMap } from '../hooks/useTripMap'
import type { MapView } from '../map/tripLayers'
import type { Trip } from '../types/trip'

export function TripMap({ trip, view }: { trip: Trip; view: MapView }) {
  const containerRef = useTripMap(trip, view)
  return (
    <div
      ref={containerRef}
      className="trip-map"
      aria-label="Route map"
      role="region"
    />
  )
}
