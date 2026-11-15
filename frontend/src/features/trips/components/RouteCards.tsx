import { LEVEL_COLORS } from '../risk'
import {
  byRank,
  formatDuration,
  formatMiles,
  formatRisk,
  levelBreakdown,
  levelShares,
  type LevelMiles,
} from '../routeSummary'
import type { Route } from '../types/trip'

const RANK_DIGITS = 2

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
    <li className={cardClass(route)} aria-label={`Route ${route.rank}`}>
      <CardHeading route={route} />
      {route.has_no_travel && <NoTravelWarning />}
      <RouteStats route={route} />
      <LevelBar route={route} />
      <LevelList levels={levelBreakdown(route)} />
    </li>
  )
}

function cardClass(route: Route): string {
  return route.recommended ? 'route-card is-recommended' : 'route-card'
}

function CardHeading({ route }: { route: Route }) {
  return (
    <div className="card-heading">
      <span className="rank">
        {String(route.rank).padStart(RANK_DIGITS, '0')}
      </span>
      <h3>{`Route ${route.rank}`}</h3>
      {route.recommended && <span className="badge">Recommended</span>}
    </div>
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
      <Stat term="Distance" value={formatMiles(route.length_miles)} />
      <Stat term="Duration" value={formatDuration(route.duration_s)} />
      <Stat
        term="Average risk"
        value={`${formatRisk(route.metrics.average_risk)} / 4`}
      />
    </dl>
  )
}

function Stat({ term, value }: { term: string; value: string }) {
  return (
    <div className="stat">
      <dt>{term}</dt>
      <dd>{value}</dd>
    </div>
  )
}

function LevelBar({ route }: { route: Route }) {
  return (
    <div className="level-bar" aria-hidden="true">
      {levelShares(route).map(({ level, percent }) => (
        <span
          key={level}
          style={{ width: `${percent}%`, background: LEVEL_COLORS[level] }}
        />
      ))}
    </div>
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
