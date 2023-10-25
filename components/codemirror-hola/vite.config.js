import { defineConfig } from 'vite'
import path from 'path';

export default defineConfig({
    build: {
        outDir: 'dist',
        emptyOutDir: true,
        minify: true,
        lib: {
            name: "hola_editor",
            fileName: "codemirror_hola_editor",
            entry: path.resolve(__dirname, 'src/index.js'),
            formats: ['iife'],
        }
    }
})