import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { createTrip } from '../api/tripsApi'

export function useCreateTrip() {
  const navigate = useNavigate()
  return useMutation({
    mutationFn: createTrip,
    onSuccess: (trip) => navigate(`/trips/${trip.id}`),
  })
}
