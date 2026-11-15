import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import type { ReactElement } from 'react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

/** Renders `ui` at "/" with a fresh query client; "/trips/:id" shows "trip page". */
export function renderWithProviders(ui: ReactElement) {
  return render(
    <QueryClientProvider client={testQueryClient()}>
      <MemoryRouter>
        <Routes>
          <Route path="/" element={ui} />
          <Route path="/trips/:id" element={<p>trip page</p>} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

function testQueryClient(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } })
}

export function jsonResponse(body: unknown, status = 200): Response {
  const headers = { 'Content-Type': 'application/json' }
  return new Response(JSON.stringify(body), { status, headers })
}
