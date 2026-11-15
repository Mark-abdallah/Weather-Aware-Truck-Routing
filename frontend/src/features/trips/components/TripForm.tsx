import { useCreateTrip } from '../hooks/useCreateTrip'
import { useTripForm } from '../hooks/useTripForm'
import { PlaceField } from './PlaceField'
import { TripDetailsFields } from './TripDetailsFields'

export function TripForm() {
  const createTrip = useCreateTrip()
  const form = useTripForm(createTrip.mutate)
  return (
    <form onSubmit={form.submit} noValidate aria-label="Plan a trip">
      <PlaceField label="Origin" name="origin" form={form} />
      <PlaceField label="Destination" name="destination" form={form} />
      <TripDetailsFields form={form} />
      <SubmitRow pending={createTrip.isPending} error={createTrip.error} />
    </form>
  )
}

function SubmitRow({
  pending,
  error,
}: {
  pending: boolean
  error: Error | null
}) {
  return (
    <div>
      <button type="submit" disabled={pending}>
        {pending ? 'Planning routes…' : 'Plan routes'}
      </button>
      {error && <p role="alert">{error.message}</p>}
    </div>
  )
}
