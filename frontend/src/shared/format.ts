export function formatDateTime(iso: string): string {
  const options = { dateStyle: 'medium', timeStyle: 'short' } as const
  return new Date(iso).toLocaleString(undefined, options)
}
