import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'
import App from './App'

it('renders the brand and the trip planner', () => {
  render(<App />)
  expect(screen.getByRole('link', { name: 'Spotter home' })).toBeInTheDocument()
  expect(screen.getByRole('form', { name: 'Plan a trip' })).toBeInTheDocument()
})
