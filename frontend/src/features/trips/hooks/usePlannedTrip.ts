import { useLocation } from 'react-router-dom'
import type { Trip } from '../types/trip'

export const TRIP_PATH = '/trip'

export function usePlannedTrip(): Trip | null {
  const { state } = useLocation()
  return (state as Trip | null) ?? null
}
