import type { ChangeEvent } from 'react'
import { formatDateTime } from '../../../shared/format'
import { LEVEL_COLORS, LEVEL_LABELS } from '../risk'
import { LEVEL_ORDER } from '../routeSummary'

interface HeatmapSliderProps {
  hours: string[]
  hourIndex: number
  onChange: (hourIndex: number) => void
}

export function HeatmapSlider({
  hours,
  hourIndex,
  onChange,
}: HeatmapSliderProps) {
  const label = `+${hourIndex} h · ${formatDateTime(hours[hourIndex])}`
  return (
    <label className="heatmap-slider">
      <span>{`Heatmap: ${label}`}</span>
      <HourRange hours={hours} hourIndex={hourIndex} onChange={onChange} />
    </label>
  )
}

function HourRange({ hours, hourIndex, onChange }: HeatmapSliderProps) {
  const change = (event: ChangeEvent<HTMLInputElement>) =>
    onChange(Number(event.target.value))
  const bounds = { min: 0, max: hours.length - 1, step: 1 }
  return <input type="range" {...bounds} value={hourIndex} onChange={change} />
}

export function RiskLegend() {
  return (
    <ul className="risk-legend" aria-label="Risk levels">
      {LEVEL_ORDER.map((level) => (
        <li key={level} style={{ borderLeftColor: LEVEL_COLORS[level] }}>
          {LEVEL_LABELS[level]}
        </li>
      ))}
    </ul>
  )
}
