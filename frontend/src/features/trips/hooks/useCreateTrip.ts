import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { createTrip } from '../api/tripsApi'
import { TRIP_PATH } from './usePlannedTrip'

export function useCreateTrip() {
  const navigate = useNavigate()
  return useMutation({
    mutationFn: createTrip,
    onSuccess: (trip) => navigate(TRIP_PATH, { state: trip }),
  })
}
