import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { formatDateTime } from '../../../shared/format'
import { HeatmapSlider, RiskLegend } from './HeatmapControls'

const HOURS = Array.from({ length: 49 }, (_, hour) =>
  new Date(Date.UTC(2026, 0, 1, hour)).toISOString(),
)

it('spans 0 to 48 hours and reports the chosen hour', () => {
  const onChange = vi.fn()
  render(<HeatmapSlider hours={HOURS} hourIndex={3} onChange={onChange} />)
  const slider = screen.getByRole('slider')
  expect(slider).toHaveAttribute('min', '0')
  expect(slider).toHaveAttribute('max', '48')
  expect(
    screen.getByText(`Heatmap: +3 h · ${formatDateTime(HOURS[3])}`),
  ).toBeInTheDocument()
  fireEvent.change(slider, { target: { value: '10' } })
  expect(onChange).toHaveBeenCalledWith(10)
})

it('lists all five risk levels', () => {
  render(<RiskLegend />)
  expect(
    screen.getAllByRole('listitem').map((item) => item.textContent),
  ).toEqual(['Low', 'Moderate', 'High', 'Severe', 'No Travel'])
})
