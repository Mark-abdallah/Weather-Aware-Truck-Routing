import { Link, useParams } from 'react-router-dom'
import { formatDateTime } from '../../../shared/format'
import { useTrip } from '../hooks/useTrip'
import type { Trip } from '../types/trip'
import { RouteCards } from './RouteCards'
import { TripMap } from './TripMap'

export function TripPage() {
  const { id = '' } = useParams()
  const trip = useTrip(id)
  if (trip.isPending) return <p role="status">Loading trip…</p>
  if (trip.isError) return <p role="alert">{trip.error.message}</p>
  return <TripView trip={trip.data} />
}

function TripView({ trip }: { trip: Trip }) {
  return (
    <section aria-label="Trip">
      <TripHeader trip={trip} />
      <TripMap routes={trip.plan.routes} />
      <RouteCards routes={trip.plan.routes} />
      <Link to="/">Plan another trip</Link>
    </section>
  )
}

function TripHeader({ trip }: { trip: Trip }) {
  const { origin, destination } = trip.inputs
  return (
    <header>
      <h2>{`${origin.label} → ${destination.label}`}</h2>
      <p>{`Computed at ${formatDateTime(trip.computed_at)}`}</p>
      {trip.plan.notice && <p role="status">{trip.plan.notice}</p>}
    </header>
  )
}
