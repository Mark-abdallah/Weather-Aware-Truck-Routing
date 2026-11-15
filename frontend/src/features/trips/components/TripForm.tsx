import { ErrorText } from '../../../shared/components/ErrorText'
import { useCreateTrip } from '../hooks/useCreateTrip'
import { useTripForm, type TripFormState } from '../hooks/useTripForm'
import { PlaceField } from './PlaceField'
import { TripDetailsFields } from './TripDetailsFields'

const FORM_ATTRIBUTES = {
  className: 'trip-form card',
  noValidate: true,
  'aria-label': 'Plan a trip',
}

export function TripForm() {
  const createTrip = useCreateTrip()
  const form = useTripForm(createTrip.mutate)
  return (
    <form {...FORM_ATTRIBUTES} onSubmit={form.submit}>
      <PlaceFields form={form} />
      <TripDetailsFields form={form} />
      <SubmitRow pending={createTrip.isPending} error={createTrip.error} />
    </form>
  )
}

function PlaceFields({ form }: { form: TripFormState }) {
  return (
    <div className="form-row">
      <PlaceField label="Origin" name="origin" form={form} />
      <PlaceField label="Destination" name="destination" form={form} />
    </div>
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
    <div className="form-actions">
      <ErrorText className="form-error" message={error?.message} />
      <button className="btn-primary" type="submit" disabled={pending}>
        {pending ? 'Planning routes…' : 'Plan routes'}
      </button>
    </div>
  )
}
