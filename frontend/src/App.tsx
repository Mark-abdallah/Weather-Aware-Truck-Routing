import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { PlannerPage } from './features/trips/components/PlannerPage'
import { TripPage } from './features/trips/components/TripPage'
import { AppShell } from './shared/components/AppShell'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppShell>
          <AppRoutes />
        </AppShell>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<PlannerPage />} />
      <Route path="/trips/:id" element={<TripPage />} />
    </Routes>
  )
}
