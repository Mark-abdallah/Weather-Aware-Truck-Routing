import { LEVEL_COLORS } from '../risk'
import {
  byRank,
  formatDuration,
  formatMiles,
  formatRisk,
  levelBreakdown,
  type LevelMiles,
} from '../routeSummary'
import type { Route } from '../types/trip'

export function RouteCards({ routes }: { routes: Route[] }) {
  return (
    <ol className="route-cards" aria-label="Routes">
      {byRank(routes).map((route) => (
        <RouteCard key={route.route_id} route={route} />
      ))}
    </ol>
  )
}

function RouteCard({ route }: { route: Route }) {
  return (
    <li className="route-card" aria-label={`Route ${route.rank}`}>
      <h3>{`Route ${route.rank}`}</h3>
      {route.recommended && <span className="badge">Recommended</span>}
      {route.has_no_travel && <NoTravelWarning />}
      <RouteStats route={route} />
      <LevelList levels={levelBreakdown(route)} />
    </li>
  )
}

function NoTravelWarning() {
  return (
    <p className="warning" role="note">
      Warning: part of this route is rated No Travel.
    </p>
  )
}

function RouteStats({ route }: { route: Route }) {
  return (
    <dl className="route-stats">
      <dt>Distance</dt>
      <dd>{formatMiles(route.length_miles)}</dd>
      <dt>Duration</dt>
      <dd>{formatDuration(route.duration_s)}</dd>
      <dt>Average risk</dt>
      <dd>{`${formatRisk(route.metrics.average_risk)} / 4`}</dd>
    </dl>
  )
}

function LevelList({ levels }: { levels: LevelMiles[] }) {
  return (
    <ul className="level-list" aria-label="Miles by risk level">
      {levels.map(({ level, label, miles }) => (
        <li key={level} style={{ borderLeftColor: LEVEL_COLORS[level] }}>
          {`${label}: ${miles}`}
        </li>
      ))}
    </ul>
  )
}
