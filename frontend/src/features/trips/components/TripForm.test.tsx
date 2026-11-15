import { fireEvent, screen } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import {
  jsonResponse,
  renderWithProviders,
} from '../../../test/renderWithProviders'
import { makeTrip } from '../../../test/tripFixture'
import { TripForm } from './TripForm'

const DENVER = { label: 'Denver, CO, United States', lat: 39.74, lon: -104.99 }
const KC = { label: 'Kansas City, MO, United States', lat: 39.1, lon: -94.58 }
let fetchMock: ReturnType<typeof vi.fn>

function respond(url: string, init?: RequestInit): Response {
  if (url.includes('/api/autosuggest')) {
    const query = new URL(url).searchParams.get('q') ?? ''
    return jsonResponse(query.startsWith('Den') ? [DENVER] : [KC])
  }
  if (init?.method === 'POST') return jsonResponse(makeTrip(), 201)
  return jsonResponse({ detail: 'unexpected' }, 500)
}

beforeEach(() => {
  fetchMock = vi.fn((url: string, init?: RequestInit) =>
    Promise.resolve(respond(url, init)),
  )
  vi.stubGlobal('fetch', fetchMock)
})
afterEach(() => vi.unstubAllGlobals())

async function choosePlace(
  label: string,
  text: string,
  place: { label: string },
) {
  fireEvent.change(screen.getByLabelText(label), { target: { value: text } })
  fireEvent.click(await screen.findByRole('button', { name: place.label }))
}

it('shows validation errors and sends nothing when empty', () => {
  renderWithProviders(<TripForm />)
  fireEvent.click(screen.getByRole('button', { name: 'Plan routes' }))
  expect(
    screen.getByText('Choose an origin from the suggestions'),
  ).toBeInTheDocument()
  expect(
    screen.getByText('Enter a gross weight greater than 0'),
  ).toBeInTheDocument()
  expect(fetchMock).not.toHaveBeenCalled()
})

it('submits chosen places and navigates to the trip', async () => {
  renderWithProviders(<TripForm />)
  await choosePlace('Origin', 'Denver', DENVER)
  await choosePlace('Destination', 'Kansas', KC)
  fireEvent.change(screen.getByLabelText('Gross weight (lb)'), {
    target: { value: '35000' },
  })
  fireEvent.click(screen.getByRole('button', { name: 'Plan routes' }))
  expect(await screen.findByText('trip page')).toBeInTheDocument()
  const [, init] = fetchMock.mock.calls.find(
    ([, options]) => options?.method === 'POST',
  )!
  expect(JSON.parse(init.body)).toMatchObject({
    origin: DENVER,
    destination: KC,
    gross_weight_lb: 35000,
    interval_mi: 25,
  })
})

it('typing after choosing clears the chosen place', async () => {
  renderWithProviders(<TripForm />)
  await choosePlace('Origin', 'Denver', DENVER)
  fireEvent.change(screen.getByLabelText('Origin'), {
    target: { value: 'Denv' },
  })
  fireEvent.click(screen.getByRole('button', { name: 'Plan routes' }))
  expect(
    screen.getByText('Choose an origin from the suggestions'),
  ).toBeInTheDocument()
})

it('shows the server error message', async () => {
  fetchMock.mockImplementation((url: string, init?: RequestInit) =>
    Promise.resolve(
      init?.method === 'POST'
        ? jsonResponse(
            { detail: 'Weather service unavailable, try again' },
            502,
          )
        : respond(url, init),
    ),
  )
  renderWithProviders(<TripForm />)
  await choosePlace('Origin', 'Denver', DENVER)
  await choosePlace('Destination', 'Kansas', KC)
  fireEvent.change(screen.getByLabelText('Gross weight (lb)'), {
    target: { value: '35000' },
  })
  fireEvent.click(screen.getByRole('button', { name: 'Plan routes' }))
  expect(
    await screen.findByText('Weather service unavailable, try again'),
  ).toBeInTheDocument()
})
