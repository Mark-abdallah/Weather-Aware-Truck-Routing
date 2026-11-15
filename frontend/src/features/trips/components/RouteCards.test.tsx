import { render, screen, within } from '@testing-library/react'
import { expect, it } from 'vitest'
import { makeRoute } from '../../../test/tripFixture'
import { formatDuration } from '../routeSummary'
import { RouteCards } from './RouteCards'

const SAFE = makeRoute({ route_id: 'safe', rank: 1, recommended: true })
const RISKY = makeRoute({
  route_id: 'risky',
  rank: 2,
  recommended: false,
  has_no_travel: true,
  length_miles: 250,
  duration_s: 4 * 3600 + 5 * 60,
  metrics: {
    total_miles: 250,
    average_risk: 1.234,
    miles_by_level: { low: 200, no_travel: 50, high: 0 },
  },
})

it('lists routes by rank with the recommended badge on the first', () => {
  render(<RouteCards routes={[RISKY, SAFE]} />)
  const cards = screen.getAllByRole('listitem', { name: /^Route \d$/ })
  expect(cards.map((card) => card.getAttribute('aria-label'))).toEqual([
    'Route 1',
    'Route 2',
  ])
  expect(within(cards[0]).getByText('Recommended')).toBeInTheDocument()
  expect(within(cards[1]).queryByText('Recommended')).toBeNull()
})

it('shows stats, non-zero levels in order and the No Travel warning', () => {
  render(<RouteCards routes={[RISKY]} />)
  const card = screen.getByRole('listitem', { name: 'Route 2' })
  expect(within(card).getByText('250.0 mi')).toBeInTheDocument()
  expect(within(card).getByText('4 h 5 min')).toBeInTheDocument()
  expect(within(card).getByText('1.23 / 4')).toBeInTheDocument()
  const levels = within(card).getByRole('list', { name: 'Miles by risk level' })
  expect(
    within(levels)
      .getAllByRole('listitem')
      .map((item) => item.textContent),
  ).toEqual(['Low: 200.0 mi', 'No Travel: 50.0 mi'])
  expect(within(card).getByRole('note')).toHaveTextContent('No Travel')
})

it.each([
  [45 * 60, '45 min'],
  [3600, '1 h 0 min'],
  [8.5 * 3600, '8 h 30 min'],
])('formats %d seconds as %s', (seconds, expected) => {
  expect(formatDuration(seconds)).toBe(expected)
})
