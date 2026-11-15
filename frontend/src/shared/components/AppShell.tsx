import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="shell">
      <Topbar />
      <main className="page">{children}</main>
    </div>
  )
}

function Topbar() {
  return (
    <header className="topbar">
      <Link to="/" className="brand" aria-label="Spotter home">
        <span className="brand-mark" aria-hidden="true" />
        Spotter
      </Link>
      <span className="topbar-tag">Weather-intelligent freight routing</span>
    </header>
  )
}
