import { formatDateTime } from '../../../shared/format'
import { LEVEL_LABELS } from '../risk'
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

/** Built with textContent (never innerHTML) so data cannot inject markup. */
export function checkpointPopupContent(checkpoint: Checkpoint): HTMLElement {
  const container = document.createElement('div')
  for (const line of checkpointLines(checkpoint)) {
    const paragraph = document.createElement('p')
    paragraph.textContent = line
    container.append(paragraph)
  }
  return container
}
