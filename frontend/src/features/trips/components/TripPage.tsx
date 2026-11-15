import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { formatDateTime } from '../../../shared/format'
import {
  useRouteSelection,
  type RouteSelection,
} from '../hooks/useRouteSelection'
import { usePlannedTrip } from '../hooks/usePlannedTrip'
import type { MapView } from '../map/tripLayers'
import type { Heatmap, Trip } from '../types/trip'
import { HeatmapSlider, RiskLegend } from './HeatmapControls'
import { RouteCards } from './RouteCards'
import { TripMap } from './TripMap'

interface SectionProps {
  trip: Trip
  selection: RouteSelection
}

export function TripPage() {
  const trip = usePlannedTrip()
  if (!trip) return <Navigate to="/" replace />
  return <TripView trip={trip} />
}

function TripView({ trip }: { trip: Trip }) {
  const selection = useRouteSelection(trip.plan.routes)
  return (
    <section className="trip" aria-label="Trip">
      <TripHeader trip={trip} />
      <div className="trip-grid">
        <TripMapSection trip={trip} selection={selection} />
        <RoutePanel trip={trip} selection={selection} />
      </div>
    </section>
  )
}

function RoutePanel({ trip, selection }: SectionProps) {
  return (
    <aside className="route-panel" aria-label="Route options">
      <p className="panel-hint">Select a route to view it on the map</p>
      <RouteCards routes={trip.plan.routes} selection={selection} />
    </aside>
  )
}

function TripHeader({ trip }: { trip: Trip }) {
  return (
    <header className="trip-header">
      <TripTitle trip={trip} />
      <Link className="btn-ghost" to="/">
        Plan another trip
      </Link>
    </header>
  )
}

function TripTitle({ trip }: { trip: Trip }) {
  const { origin, destination } = trip.inputs
  return (
    <div>
      <p className="eyebrow">Trip plan</p>
      <h2>{`${origin.label} → ${destination.label}`}</h2>
      <TripMeta trip={trip} />
    </div>
  )
}

function TripMeta({ trip }: { trip: Trip }) {
  const { inputs, plan, computed_at } = trip
  return (
    <ul className="meta-chips">
      <li>{`Departs ${formatDateTime(inputs.departure)}`}</li>
      <li>{`${inputs.gross_weight_lb.toLocaleString()} lb gross`}</li>
      <li>{`Checkpoint every ${inputs.interval_mi} mi`}</li>
      <li>{`Computed ${formatDateTime(computed_at)}`}</li>
      {plan.notice && <li role="status">{plan.notice}</li>}
    </ul>
  )
}

function TripMapSection({ trip, selection }: SectionProps) {
  const [hourIndex, setHourIndex] = useState(0)
  const overlay = { heatmap: trip.heatmap, hourIndex, onChange: setHourIndex }
  return (
    <div className="map-panel">
      <TripMap trip={trip} view={mapView(hourIndex, selection)} />
      <MapOverlay {...overlay} />
    </div>
  )
}

function mapView(hourIndex: number, selection: RouteSelection): MapView {
  return {
    hourIndex,
    selectedId: selection.selectedId,
    onSelectRoute: selection.select,
  }
}

interface MapOverlayProps {
  heatmap: Heatmap
  hourIndex: number
  onChange: (hourIndex: number) => void
}

function MapOverlay({ heatmap, hourIndex, onChange }: MapOverlayProps) {
  const slider = { hours: heatmap.hours, hourIndex, onChange }
  return (
    <div className="map-overlay card">
      <HeatmapSlider {...slider} />
      <RiskLegend />
    </div>
  )
}
