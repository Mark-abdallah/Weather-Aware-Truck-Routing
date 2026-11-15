import { getJson, postJson } from '../../../shared/api/http'
import type { Place, Trip, TripInput } from '../types/trip'

export function createTrip(input: TripInput): Promise<Trip> {
  return postJson<Trip>('/api/trips', input)
}

export function fetchSuggestions(
  query: string,
  signal?: AbortSignal,
): Promise<Place[]> {
  const params = new URLSearchParams({ q: query })
  return getJson<Place[]>(`/api/autosuggest?${params}`, signal)
}
