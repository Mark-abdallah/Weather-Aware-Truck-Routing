import type { ChangeEvent } from 'react'
import { Field } from '../../../shared/components/Field'
import type { TripFormState } from '../hooks/useTripForm'
import { INTERVAL_OPTIONS, MAX_GROSS_WEIGHT_LB, toInterval } from '../tripForm'

type TextKey = 'departureLocal' | 'grossWeight'

export function TripDetailsFields({ form }: { form: TripFormState }) {
  return (
    <div className="form-row form-row-3">
      <DepartureField form={form} />
      <WeightField form={form} />
      <IntervalField form={form} />
    </div>
  )
}

function textInput(form: TripFormState, key: TextKey) {
  const onChange = (event: ChangeEvent<HTMLInputElement>) =>
    form.setField(key, event.target.value)
  return { value: form.values[key], onChange }
}

function DepartureField({ form }: { form: TripFormState }) {
  return (
    <Field label="Departure" error={form.errors.departureLocal}>
      <input type="datetime-local" {...textInput(form, 'departureLocal')} />
    </Field>
  )
}

function WeightField({ form }: { form: TripFormState }) {
  const input = textInput(form, 'grossWeight')
  return (
    <Field label="Gross weight (lb)" error={form.errors.grossWeight}>
      <input type="number" min={1} max={MAX_GROSS_WEIGHT_LB} {...input} />
    </Field>
  )
}

function IntervalField({ form }: { form: TripFormState }) {
  const change = (event: ChangeEvent<HTMLSelectElement>) =>
    form.setField('interval', toInterval(event.target.value))
  return (
    <Field label="Checkpoint every">
      <select value={form.values.interval} onChange={change}>
        {INTERVAL_OPTIONS.map(intervalOption)}
      </select>
    </Field>
  )
}

function intervalOption(miles: number) {
  return <option key={miles} value={miles}>{`${miles} miles`}</option>
}
