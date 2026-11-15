import { describe, expect, it } from 'vitest'
import {
  initialValues,
  toLocalInputValue,
  toTripInput,
  validateTripForm,
  type TripFormValues,
} from './tripForm'

const NOW = new Date(2026, 0, 10, 12, 30)
const HOUR_MS = 60 * 60 * 1000
const DENVER = { label: 'Denver', lat: 39.74, lon: -104.99 }
const KC = { label: 'Kansas City', lat: 39.1, lon: -94.58 }

function values(overrides: Partial<TripFormValues> = {}): TripFormValues {
  const departureLocal = toLocalInputValue(new Date(NOW.getTime() + HOUR_MS))
  const base = {
    origin: DENVER,
    destination: KC,
    departureLocal,
    grossWeight: '30000',
    interval: 25 as const,
  }
  return { ...base, ...overrides }
}

function at(offsetMs: number): string {
  return toLocalInputValue(new Date(NOW.getTime() + offsetMs))
}

describe('validateTripForm', () => {
  it('accepts valid values', () => {
    expect(validateTripForm(values(), NOW)).toEqual({})
  })

  it.each([
    ['0', 'greater than 0'],
    ['', 'greater than 0'],
    ['abc', 'greater than 0'],
    ['80001', 'at most 80,000'],
  ])('rejects weight %j', (grossWeight, message) => {
    expect(
      validateTripForm(values({ grossWeight }), NOW).grossWeight,
    ).toContain(message)
  })

  it('accepts the maximum weight', () => {
    expect(validateTripForm(values({ grossWeight: '80000' }), NOW)).toEqual({})
  })

  it.each([
    [-HOUR_MS - 60_000, 'at most 1 hour ago'],
    [24 * HOUR_MS + 60_000, 'within 24 hours'],
  ])('rejects departure offset %d ms', (offset, message) => {
    expect(
      validateTripForm(values({ departureLocal: at(offset) }), NOW)
        .departureLocal,
    ).toContain(message)
  })

  it('requires chosen places that differ', () => {
    expect(validateTripForm(values({ origin: null }), NOW).origin).toBeDefined()
    expect(
      validateTripForm(values({ destination: null }), NOW).destination,
    ).toBeDefined()
    expect(
      validateTripForm(values({ destination: DENVER }), NOW).destination,
    ).toContain('differ')
  })
})

describe('form conversion', () => {
  it('defaults departure to the next full hour and interval to 25', () => {
    const initial = initialValues(NOW)
    expect(initial.departureLocal).toBe('2026-01-10T13:00')
    expect(initial.interval).toBe(25)
  })

  it('builds the API input with a UTC ISO departure', () => {
    const input = toTripInput(values())
    expect(input.departure).toBe(
      new Date(NOW.getTime() + HOUR_MS).toISOString(),
    )
    expect(input).toMatchObject({
      origin: DENVER,
      destination: KC,
      gross_weight_lb: 30000,
      interval_mi: 25,
    })
  })
})
