import { useQuery } from '@tanstack/react-query'
import { ApiError } from '../../../shared/api/http'
import { fetchTrip } from '../api/tripsApi'

const MAX_RETRIES = 2
const CLIENT_ERROR_MIN = 400
const CLIENT_ERROR_MAX = 499

/** A stored trip never changes, so it is cached forever; 4xx errors are not retried. */
export function useTrip(id: string) {
  return useQuery({
    queryKey: ['trip', id],
    queryFn: () => fetchTrip(id),
    staleTime: Infinity,
    retry: (failures, error) => failures < MAX_RETRIES && !isClientError(error),
  })
}

function isClientError(error: Error): boolean {
  const status = error instanceof ApiError ? error.status : 0
  return status >= CLIENT_ERROR_MIN && status <= CLIENT_ERROR_MAX
}
