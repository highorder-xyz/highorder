import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    server: {
        port: 15000,
        proxy: {
            // string shorthand
            '/service': 'http://127.0.0.1:5000',
            '/static': 'http://127.0.0.1:5000',
        }
    },
    publicDir: '../app/public',
    plugins: [vue()],
})
