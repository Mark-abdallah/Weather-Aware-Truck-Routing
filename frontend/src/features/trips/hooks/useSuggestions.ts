import { useQuery } from '@tanstack/react-query'
import { useDebouncedValue } from '../../../shared/hooks/useDebouncedValue'
import { fetchSuggestions } from '../api/tripsApi'

export const MIN_QUERY_LENGTH = 3
export const SUGGESTION_DEBOUNCE_MS = 300
const SUGGESTION_STALE_MS = 5 * 60 * 1000

export function useSuggestions(text: string, enabled: boolean) {
  const query = useDebouncedValue(text.trim(), SUGGESTION_DEBOUNCE_MS)
  return useQuery({
    queryKey: ['suggestions', query],
    queryFn: ({ signal }) => fetchSuggestions(query, signal),
    enabled: enabled && query.length >= MIN_QUERY_LENGTH,
    staleTime: SUGGESTION_STALE_MS,
  })
}
