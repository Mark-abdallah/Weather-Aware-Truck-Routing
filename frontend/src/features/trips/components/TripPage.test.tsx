import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { expect, it, vi } from 'vitest'
import { makeTrip } from '../../../test/tripFixture'
import type { Trip } from '../types/trip'
import { TripPage } from './TripPage'

vi.mock('./TripMap', () => ({ TripMap: () => <div>map</div> }))

function renderTrip(trip: Trip | null) {
  const entry = { pathname: '/trip', state: trip }
  return render(
    <MemoryRouter initialEntries={[entry]}>
      <Routes>
        <Route path="/" element={<p>planner</p>} />
        <Route path="/trip" element={<TripPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

it('shows the planned trip passed from the planner', () => {
  const notice = 'Only 2 route(s) available'
  renderTrip(makeTrip({ plan: { notice, routes: [] } }))
  const heading = screen.getByRole('heading', { name: 'Denver → Kansas City' })
  expect(heading).toBeInTheDocument()
  expect(screen.getByText(notice)).toBeInTheDocument()
  expect(screen.getByText(/^Computed /)).toBeInTheDocument()
})

it('goes back to the planner when there is no trip', () => {
  renderTrip(null)
  expect(screen.getByText('planner')).toBeInTheDocument()
})
