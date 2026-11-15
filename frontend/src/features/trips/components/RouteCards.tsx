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
import type { RouteSelection } from '../hooks/useRouteSelection'
import type { Route } from '../types/trip'

const RANK_DIGITS = 2

interface CardProps {
  route: Route
  selection: RouteSelection
}

export function RouteCards({
  routes,
  selection,
}: {
  routes: Route[]
  selection: RouteSelection
}) {
  return (
    <ol className="route-cards" aria-label="Routes">
      {byRank(routes).map((route) => (
        <RouteCard key={route.route_id} route={route} selection={selection} />
      ))}
    </ol>
  )
}

function RouteCard({ route, selection }: CardProps) {
  const className = cardClass(route, selection.selectedId)
  return (
    <li className={className} aria-label={`Route ${route.rank}`}>
      <SelectButton route={route} selection={selection} />
      <CardBody route={route} />
    </li>
  )
}

function CardBody({ route }: { route: Route }) {
  return (
    <>
      <CardHeading route={route} />
      {route.has_no_travel && <NoTravelWarning />}
      <RouteStats route={route} />
      <LevelBar route={route} />
      <LevelList levels={levelBreakdown(route)} />
    </>
  )
}

/** Stretched over the whole card so any click on it selects the route. */
function SelectButton({ route, selection }: CardProps) {
  const button = {
    'aria-pressed': route.route_id === selection.selectedId,
    'aria-label': `Show Route ${route.rank} on the map`,
    onClick: () => selection.select(route.route_id),
  }
  return <button type="button" className="card-select" {...button} />
}

function cardClass(route: Route, selectedId: string): string {
  const classes = ['route-card']
  if (route.recommended) classes.push('is-recommended')
  if (route.route_id === selectedId) classes.push('is-selected')
  return classes.join(' ')
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
