import type { ReactNode } from 'react'
import { ErrorText } from './ErrorText'

interface FieldProps {
  label: string
  error?: string
  children: ReactNode
}

export function Field({ label, error, children }: FieldProps) {
  return (
    <div className="field">
      <label>
        <span className="field-label">{label}</span>
        {children}
      </label>
      <ErrorText message={error} />
    </div>
  )
}
