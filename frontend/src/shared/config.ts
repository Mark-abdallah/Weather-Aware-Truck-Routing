const DEFAULT_API_URL = 'http://localhost:8000'
const TRAILING_SLASHES = /\/+$/

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_URL ?? DEFAULT_API_URL
).replace(TRAILING_SLASHES, '')
