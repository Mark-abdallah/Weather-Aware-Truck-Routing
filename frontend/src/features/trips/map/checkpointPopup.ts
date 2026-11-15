import { formatDateTime } from '../../../shared/format'
import { LEVEL_COLORS, LEVEL_LABELS } from '../risk'
import type { Checkpoint } from '../types/trip'

const MPH_DECIMALS = 0
const PRECIP_DECIMALS = 2
const MILE_DECIMALS = 1

export function checkpointLines(checkpoint: Checkpoint): string[] {
  const { wind_mph, gust_mph, rain_in_hr, snow_in_hr } = checkpoint
  return [
    `ETA ${formatDateTime(checkpoint.eta_utc)} · mile ${checkpoint.mile.toFixed(MILE_DECIMALS)}`,
    `Wind ${wind_mph.toFixed(MPH_DECIMALS)} mph (gusts ${gust_mph.toFixed(MPH_DECIMALS)} mph)`,
    `Rain ${rain_in_hr.toFixed(PRECIP_DECIMALS)} in/hr · Snow ${snow_in_hr.toFixed(PRECIP_DECIMALS)} in/hr`,
    riskLine(checkpoint),
    ...(checkpoint.load_rule_applied
      ? ['Load weight raised the wind risk']
      : []),
  ]
}

function riskLine({ level_name, causes }: Checkpoint): string {
  const label = LEVEL_LABELS[level_name]
  return causes.length
    ? `Risk: ${label} (${causes.join(', ')})`
    : `Risk: ${label}`
}

export function checkpointPopupContent(checkpoint: Checkpoint): HTMLElement {
  const container = document.createElement('div')
  container.append(
    levelChip(checkpoint),
    ...checkpointLines(checkpoint).map(paragraph),
  )
  return container
}

function levelChip({ level_name }: Checkpoint): HTMLElement {
  const chip = document.createElement('span')
  chip.className = 'popup-level'
  chip.textContent = LEVEL_LABELS[level_name]
  chip.style.background = LEVEL_COLORS[level_name]
  return chip
}

function paragraph(text: string): HTMLElement {
  const element = document.createElement('p')
  element.textContent = text
  return element
}
