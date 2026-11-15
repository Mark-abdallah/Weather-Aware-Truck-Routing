interface ErrorTextProps {
  message?: string
  className?: string
}

export function ErrorText({
  message,
  className = 'field-error',
}: ErrorTextProps) {
  if (!message) return null
  return (
    <p className={className} role="alert">
      {message}
    </p>
  )
}
