import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
    server: {
        proxy: {
            // string shorthand
            '/service': 'http://building.dev.highorder.xyz',
            '/static': 'http://building.dev.highorder.xyz',
        }
    },
    publicDir: '../app/public',
    plugins: [
        vue()
    ]
})
