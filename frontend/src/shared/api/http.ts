import { API_BASE_URL } from '../config'

const GENERIC_ERROR = 'Something went wrong, try again'
const NETWORK_ERROR = 'Cannot reach the server, check your connection'
const NETWORK_STATUS = 0

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export function getJson<T>(path: string, signal?: AbortSignal): Promise<T> {
  return request<T>(path, { signal })
}

export function postJson<T>(path: string, body: unknown): Promise<T> {
  const headers = { 'Content-Type': 'application/json' }
  return request<T>(path, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init).catch(
    (error: unknown) => {
      if (init.signal?.aborted) throw error
      throw new ApiError(NETWORK_STATUS, NETWORK_ERROR)
    },
  )
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, errorMessage(body))
  return body as T
}

/** First message in a DRF error body: {"detail": ...} or nested field errors. */
export function errorMessage(body: unknown): string {
  return firstMessage(body) ?? GENERIC_ERROR
}

function firstMessage(value: unknown): string | undefined {
  if (typeof value === 'string') return value
  if (value === null || typeof value !== 'object') return undefined
  for (const item of Object.values(value)) {
    const message = firstMessage(item)
    if (message) return message
  }
  return undefined
}
