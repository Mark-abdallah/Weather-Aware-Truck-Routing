import { expect, it } from 'vitest'
import { formatDateTime } from '../../../shared/format'
import { makeCheckpoint } from '../../../test/tripFixture'
import { checkpointLines, checkpointPopupContent } from './checkpointPopup'

it('lists ETA, conditions, level and all tied causes', () => {
  const lines = checkpointLines(makeCheckpoint())
  expect(lines).toEqual([
    `ETA ${formatDateTime('2026-01-01T12:00:00+00:00')} · mile 25.0`,
    'Wind 30 mph (gusts 41 mph)',
    'Rain 0.10 in/hr · Snow 0.00 in/hr',
    'Risk: Moderate (wind, rain)',
  ])
})

it('mentions the load rule and omits empty causes', () => {
  const lines = checkpointLines(
    makeCheckpoint({ level_name: 'low', causes: [], load_rule_applied: true }),
  )
  expect(lines.slice(3)).toEqual([
    'Risk: Low',
    'Load weight raised the wind risk',
  ])
})

it('renders text safely without interpreting markup', () => {
  const element = checkpointPopupContent(makeCheckpoint())
  expect(element.querySelectorAll('p')).toHaveLength(4)
  expect(element.querySelector('script')).toBeNull()
})
