import { screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { jsonResponse, renderAt } from '../../../test/renderWithProviders'
import { makeTrip } from '../../../test/tripFixture'
import { TripPage } from './TripPage'

vi.mock('./TripMap', () => ({ TripMap: () => <div>map</div> }))

afterEach(() => vi.unstubAllGlobals())

function serve(response: Response) {
  const fetchMock = vi.fn().mockResolvedValue(response)
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

it('loads the trip by id and shows its summary', async () => {
  const fetchMock = serve(
    jsonResponse(
      makeTrip({ plan: { notice: 'Only 2 route(s) available', routes: [] } }),
    ),
  )
  renderAt(<TripPage />, { pattern: '/trips/:id', url: '/trips/trip-1' })
  expect(screen.getByRole('status')).toHaveTextContent('Loading trip')
  expect(
    await screen.findByRole('heading', { name: 'Denver → Kansas City' }),
  ).toBeInTheDocument()
  expect(screen.getByText('Only 2 route(s) available')).toBeInTheDocument()
  expect(screen.getByText(/^Computed /)).toBeInTheDocument()
  expect(fetchMock.mock.calls[0][0]).toMatch(/\/api\/trips\/trip-1$/)
})

it('shows not-found without retrying', async () => {
  const fetchMock = serve(jsonResponse({ detail: 'Trip not found.' }, 404))
  renderAt(<TripPage />, {
    pattern: '/trips/:id',
    url: '/trips/missing',
    retry: true,
  })
  expect(await screen.findByRole('alert')).toHaveTextContent('Trip not found.')
  expect(fetchMock).toHaveBeenCalledTimes(1)
})
