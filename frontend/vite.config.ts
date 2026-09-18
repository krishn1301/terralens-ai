import react from '@vitejs/plugin-react'
import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'

export default defineConfig(({ mode }) => ({
  // Static hosts that serve the app from a sub-path (for example GitHub Pages
  // project sites) set VITE_BASE_PATH such as /terralens-ai/ at build time.
  base: loadEnv(mode, '.', 'VITE_').VITE_BASE_PATH || '/',
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
  server: {
    port: 5173,
  },
}))
