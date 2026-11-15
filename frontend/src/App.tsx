import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { TripForm } from './features/trips/components/TripForm'
import { TripPage } from './features/trips/components/TripPage'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <h1>Weather-Aware Truck Routing</h1>
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<TripForm />} />
      <Route path="/trips/:id" element={<TripPage />} />
    </Routes>
  )
}
