import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { formatDateTime } from '../../../shared/format'
import { useTrip } from '../hooks/useTrip'
import type { Heatmap, Trip } from '../types/trip'
import { HeatmapSlider, RiskLegend } from './HeatmapControls'
import { RouteCards } from './RouteCards'
import { TripMap } from './TripMap'

type MessageRole = 'status' | 'alert'

export function TripPage() {
  const { id = '' } = useParams()
  const trip = useTrip(id)
  if (trip.isPending) return <PageMessage role="status" text="Loading trip…" />
  if (trip.isError)
    return <PageMessage role="alert" text={trip.error.message} />
  return <TripView trip={trip.data} />
}

function PageMessage({ role, text }: { role: MessageRole; text: string }) {
  return (
    <p className="page-message card" role={role}>
      {text}
    </p>
  )
}

function TripView({ trip }: { trip: Trip }) {
  return (
    <section className="trip" aria-label="Trip">
      <TripHeader trip={trip} />
      <div className="trip-grid">
        <TripMapSection trip={trip} />
        <RoutePanel trip={trip} />
      </div>
    </section>
  )
}

function RoutePanel({ trip }: { trip: Trip }) {
  return (
    <aside className="route-panel">
      <RouteCards routes={trip.plan.routes} />
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

function TripMapSection({ trip }: { trip: Trip }) {
  const [hourIndex, setHourIndex] = useState(0)
  const { heatmap, plan } = trip
  const hour = { hourIndex, onChange: setHourIndex }
  return (
    <div className="map-panel">
      <TripMap routes={plan.routes} heatmap={heatmap} hourIndex={hourIndex} />
      <MapOverlay heatmap={heatmap} {...hour} />
    </div>
  )
}

interface MapOverlayProps {
  heatmap: Heatmap
  hourIndex: number
  onChange: (hourIndex: number) => void
}

function MapOverlay({ heatmap, hourIndex, onChange }: MapOverlayProps) {
  return (
    <div className="map-overlay card">
      <HeatmapSlider
        hours={heatmap.hours}
        hourIndex={hourIndex}
        onChange={onChange}
      />
      <RiskLegend />
    </div>
  )
}
