import { useState, type FormEvent } from 'react'
import type { TripInput } from '../types/trip'
import {
  initialValues,
  submitIfValid,
  type TripFormErrors,
  type TripFormValues,
} from '../tripForm'

export type SetField = <K extends keyof TripFormValues>(
  key: K,
  value: TripFormValues[K],
) => void

export function useTripForm(onValid: (input: TripInput) => void) {
  const [values, setValues] = useState(() => initialValues(new Date()))
  const [errors, setErrors] = useState<TripFormErrors>({})
  const setField: SetField = (key, value) =>
    setValues((current) => ({ ...current, [key]: value }))
  const submit = (event: FormEvent) => {
    event.preventDefault()
    setErrors(submitIfValid(values, onValid))
  }
  return { values, errors, setField, submit }
}

export type TripFormState = ReturnType<typeof useTripForm>
