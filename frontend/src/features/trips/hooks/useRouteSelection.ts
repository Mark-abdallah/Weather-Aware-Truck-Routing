import { useState } from 'react'
import type { Route } from '../types/trip'

/** Which route is highlighted on the map; starts on the recommended route. */
export function useRouteSelection(routes: Route[]) {
  const initial = routes.find((route) => route.recommended) ?? routes[0]
  const [selectedId, select] = useState(initial?.route_id ?? '')
  return { selectedId, select }
}

export type RouteSelection = ReturnType<typeof useRouteSelection>
