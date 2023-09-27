import { defineConfig, searchForWorkspaceRoot  } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    server: {
        proxy: {
            // string shorthand
            '/service': 'http://127.0.0.1:5000',
            '/static': 'http://127.0.0.1:5000',
        },
        fs: {
            allow: [
              // search up for workspace root
              searchForWorkspaceRoot(process.cwd()),
              // your custom rules
              '../app/'
            ],
        },
    },
    publicDir: '../app/public',
    plugins: [
        vue()
    ]
})
