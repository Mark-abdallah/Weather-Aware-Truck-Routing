import 'maplibre-gl/dist/maplibre-gl.css'
import { useTripMap } from '../hooks/useTripMap'
import type { Heatmap, Route } from '../types/trip'

interface TripMapProps {
  routes: Route[]
  heatmap: Heatmap
  hourIndex: number
}

export function TripMap({ routes, heatmap, hourIndex }: TripMapProps) {
  const containerRef = useTripMap(routes, heatmap, hourIndex)
  return (
    <div
      ref={containerRef}
      className="trip-map"
      aria-label="Route map"
      role="region"
    />
  )
}
