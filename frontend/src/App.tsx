import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'
import { TripForm } from './features/trips/components/TripForm'

const queryClient = new QueryClient()

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <h1>Weather-Aware Truck Routing</h1>
        <TripForm />
      </BrowserRouter>
    </QueryClientProvider>
  )
}
