import { afterEach, describe, expect, it, vi } from 'vitest'
import { jsonResponse } from '../../test/renderWithProviders'
import { ApiError, errorMessage, getJson, postJson } from './http'

afterEach(() => vi.unstubAllGlobals())

describe('errorMessage', () => {
  it.each([
    [
      { detail: 'Weather service unavailable, try again' },
      'Weather service unavailable, try again',
    ],
    [
      { origin: { lat: ['Ensure this value is less than or equal to 90.'] } },
      'Ensure this value is less than or equal to 90.',
    ],
    [
      { non_field_errors: ['Origin and destination must differ.'] },
      'Origin and destination must differ.',
    ],
    [null, 'Something went wrong, try again'],
  ])('extracts the first message from %j', (body, expected) => {
    expect(errorMessage(body)).toBe(expected)
  })
})

describe('requests', () => {
  it('posts JSON and returns the parsed body', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: 'x' }, 201))
    vi.stubGlobal('fetch', fetchMock)
    await expect(postJson('/api/trips', { a: 1 })).resolves.toEqual({ id: 'x' })
    expect(fetchMock.mock.calls[0][1]).toMatchObject({
      method: 'POST',
      body: '{"a":1}',
    })
  })

  it('throws ApiError with status and server message', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ detail: 'Nope' }, 502)),
    )
    await expect(getJson('/api/x')).rejects.toEqual(new ApiError(502, 'Nope'))
  })

  it('maps network failures to a friendly ApiError', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new TypeError('Failed to fetch')),
    )
    await expect(getJson('/api/x')).rejects.toMatchObject({
      status: 0,
      message: expect.stringContaining('Cannot reach'),
    })
  })
})
