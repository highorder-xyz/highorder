import { defineConfig, searchForWorkspaceRoot } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  server: {
    proxy: {
      '/service': 'http://127.0.0.1:5000',
      '/static': 'http://127.0.0.1:5000'
    },
    fs: {
      allow: [searchForWorkspaceRoot(process.cwd()), '../app/']
    }
  },
  publicDir: '../app/public',
  plugins: [react()],
  define: {
    __SIMULATOR_VERSION__: JSON.stringify(process.env.npm_package_version)
  }
})
