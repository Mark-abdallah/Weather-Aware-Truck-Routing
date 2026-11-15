/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  // MapLibre 6 loads its worker by a URL relative to its own module; pre-bundling moves the
  // module into .vite/deps and breaks that URL ("Worker failed to load"), so serve it as-is.
  optimizeDeps: { exclude: ['maplibre-gl'] },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
})
