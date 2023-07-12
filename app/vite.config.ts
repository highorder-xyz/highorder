import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    server: {
        proxy: {
            // string shorthand
            '/service': 'http://127.0.0.1:5000/',
            '/static': 'http://127.0.0.1:5000/',
        }
    },
    resolve: {
        alias: {
            '~': resolve(__dirname, 'src'),
        },
    },
    plugins: [
        vue()
    ],
    build: {
        lib: {
            // Could also be a dictionary or array of multiple entry points
            entry: resolve(__dirname, 'src/index.ts'),
            name: '@highorder/app',
            // the proper extensions will be added
            fileName: 'highorder-app',
        },
        rollupOptions: {
            // make sure to externalize deps that shouldn't be bundled
            // into your library
            external: ['vue'],
            output: {
                // Provide global variables to use in the UMD build
                // for externalized deps
                globals: {
                    vue: 'Vue',
                },
            },
        },
    },
})
