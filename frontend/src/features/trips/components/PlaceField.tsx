import { Field } from '../../../shared/components/Field'
import { usePlaceField, type PlaceFieldState } from '../hooks/usePlaceField'
import type { TripFormState } from '../hooks/useTripForm'
import type { Place } from '../types/trip'

const SUGGESTIONS_FAILED = 'Suggestions unavailable, try again'

interface PlaceFieldProps {
  label: string
  name: 'origin' | 'destination'
  form: TripFormState
}

export function PlaceField({ label, name, form }: PlaceFieldProps) {
  const field = usePlaceField((place) => form.setField(name, place))
  return (
    <div className="place-field">
      <Field label={label} error={form.errors[name]}>
        <input {...field.input} autoComplete="off" />
      </Field>
      <SuggestionList field={field} label={label} />
    </div>
  )
}

function SuggestionList({
  field,
  label,
}: {
  field: PlaceFieldState
  label: string
}) {
  if (field.failed) return <SuggestionsUnavailable />
  if (field.options.length === 0) return null
  return (
    <ul className="suggestions" aria-label={`${label} suggestions`}>
      {field.options.map((place) => (
        <SuggestionItem key={placeKey(place)} place={place} field={field} />
      ))}
    </ul>
  )
}

function SuggestionItem({
  place,
  field,
}: {
  place: Place
  field: PlaceFieldState
}) {
  return (
    <li>
      <button type="button" onClick={() => field.choose(place)}>
        {place.label}
      </button>
    </li>
  )
}

function SuggestionsUnavailable() {
  return (
    <p className="field-hint" role="status">
      {SUGGESTIONS_FAILED}
    </p>
  )
}

function placeKey(place: Place): string {
  return `${place.lat},${place.lon},${place.label}`
}
