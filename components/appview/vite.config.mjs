import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// JS version of Vite config (no TypeScript) for the React app
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
