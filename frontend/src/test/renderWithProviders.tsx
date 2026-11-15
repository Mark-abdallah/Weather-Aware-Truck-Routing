import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

interface RenderAtOptions {
  pattern: string
  url: string
  /** Keep each hook's own retry rule instead of disabling retries. */
  retry?: boolean
}

/** Renders `ui` at "/" with a fresh query client; "/trips/:id" shows "trip page". */
export function renderWithProviders(ui: ReactElement) {
  return render(
    <QueryClientProvider client={testQueryClient(false)}>
      <MemoryRouter>
        <Routes>
          <Route path="/" element={ui} />
          <Route path="/trips/:id" element={<p>trip page</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

/** Renders `ui` for route `pattern` with the browser at `url`. */
export function renderAt(
  ui: ReactElement,
  { pattern, url, retry = false }: RenderAtOptions,
) {
  return render(
    <QueryClientProvider client={testQueryClient(retry)}>
      <MemoryRouter initialEntries={[url]}>
        <Routes>
          <Route path={pattern} element={ui} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function testQueryClient(retry: boolean): QueryClient {
  return new QueryClient({
    defaultOptions: { queries: retry ? {} : { retry: false } },
  })
}

export function jsonResponse(body: unknown, status = 200): Response {
  const headers = { 'Content-Type': 'application/json' }
  return new Response(JSON.stringify(body), { status, headers })
}
