import type { IntervalMiles, Place, TripInput } from './types/trip'

/** Trip form values, rules and conversion (mirrors the backend rules in docs/SPEC.md). */

export const MAX_GROSS_WEIGHT_LB = 80_000
export const INTERVAL_OPTIONS: readonly IntervalMiles[] = [10, 25, 50]
export const DEFAULT_INTERVAL: IntervalMiles = 25
const HOUR_MS = 60 * 60 * 1000
const MAX_DAYS_AHEAD = 7
const EARLIEST_MS_BEFORE_NOW = HOUR_MS
const LATEST_MS_AFTER_NOW = MAX_DAYS_AHEAD * 24 * HOUR_MS

export interface TripFormValues {
  origin: Place | null
  destination: Place | null
  departureLocal: string
  grossWeight: string
  interval: IntervalMiles
}

export type TripFormErrors = Partial<Record<keyof TripFormValues, string>>

export function initialValues(now: Date): TripFormValues {
  const nextHour = new Date(now)
  nextHour.setHours(now.getHours() + 1, 0, 0, 0)
  const departureLocal = toLocalInputValue(nextHour)
  return {
    origin: null,
    destination: null,
    departureLocal,
    grossWeight: '',
    interval: DEFAULT_INTERVAL,
  }
}

/** "YYYY-MM-DDTHH:mm" in the browser's time zone, as <input type="datetime-local"> expects. */
export function toLocalInputValue(date: Date): string {
  const pad = (value: number) => String(value).padStart(2, '0')
  const day = `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`
  return `${day}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function validateTripForm(
  values: TripFormValues,
  now: Date,
): TripFormErrors {
  const errors: TripFormErrors = {
    origin: values.origin ? undefined : 'Choose an origin from the suggestions',
    destination: destinationError(values),
    departureLocal: departureError(values.departureLocal, now),
    grossWeight: weightError(values.grossWeight),
  }
  return Object.fromEntries(
    Object.entries(errors).filter(([, message]) => message),
  )
}

function destinationError({
  origin,
  destination,
}: TripFormValues): string | undefined {
  if (!destination) return 'Choose a destination from the suggestions'
  const same =
    origin?.lat === destination.lat && origin?.lon === destination.lon
  return same ? 'Destination must differ from the origin' : undefined
}

function departureError(departureLocal: string, now: Date): string | undefined {
  const departure = new Date(departureLocal).getTime()
  if (Number.isNaN(departure)) return 'Enter a departure date and time'
  if (departure < now.getTime() - EARLIEST_MS_BEFORE_NOW)
    return 'Departure can be at most 1 hour ago'
  if (departure > now.getTime() + LATEST_MS_AFTER_NOW)
    return `Departure must be within ${MAX_DAYS_AHEAD} days`
  return undefined
}

function weightError(grossWeight: string): string | undefined {
  const weight = Number(grossWeight)
  if (!grossWeight.trim() || !Number.isFinite(weight) || weight <= 0)
    return 'Enter a gross weight greater than 0'
  if (weight > MAX_GROSS_WEIGHT_LB)
    return 'Gross weight must be at most 80,000 lb'
  return undefined
}

/** Call only after validateTripForm returned no errors. */
export function toTripInput(values: TripFormValues): TripInput {
  if (!values.origin || !values.destination)
    throw new Error('Places are required')
  return {
    origin: values.origin,
    destination: values.destination,
    departure: new Date(values.departureLocal).toISOString(),
    gross_weight_lb: Number(values.grossWeight),
    interval_mi: values.interval,
  }
}

/** Validate now; call onValid with the API input only when there are no errors. */
export function submitIfValid(
  values: TripFormValues,
  onValid: (input: TripInput) => void,
): TripFormErrors {
  const errors = validateTripForm(values, new Date())
  if (Object.keys(errors).length === 0) onValid(toTripInput(values))
  return errors
}

export function toInterval(value: string): IntervalMiles {
  const interval = INTERVAL_OPTIONS.find((option) => option === Number(value))
  return interval ?? DEFAULT_INTERVAL
}
