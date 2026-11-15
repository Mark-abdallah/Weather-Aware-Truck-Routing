import { TripForm } from './TripForm'

const LEDE =
  'Three truck routes, scored against the forecast at the exact hour you reach every mile — tuned to your load.'

export function PlannerPage() {
  return (
    <div className="planner">
      <Hero />
      <TripForm />
    </div>
  )
}

function Hero() {
  return (
    <section className="hero">
      <p className="eyebrow">Route intelligence</p>
      <h1>Arrive safely, whatever the sky brings.</h1>
      <p className="lede">{LEDE}</p>
    </section>
  )
}
