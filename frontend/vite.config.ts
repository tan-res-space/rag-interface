/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@shared': path.resolve(__dirname, './src/shared'),
      '@features': path.resolve(__dirname, './src/features'),
      '@infrastructure': path.resolve(__dirname, './src/infrastructure'),
      '@domain': path.resolve(__dirname, './src/domain'),
    },
  },
  server: {
    proxy: {
      // Proxy API Gateway requests (primary)
      '/api/v1/speaker-bucket-management': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy direct service requests (fallback)
      '/api/v1/speakers': {
        target: 'http://localhost:8011',
        changeOrigin: true,
        secure: false,
      },
      '/api/v1/bucket-transitions': {
        target: 'http://localhost:8011',
        changeOrigin: true,
        secure: false,
      },
      '/api/v1/ser': {
        target: 'http://localhost:8014',
        changeOrigin: true,
        secure: false,
      },
      '/api/v1/mt-validation': {
        target: 'http://localhost:8014',
        changeOrigin: true,
        secure: false,
      },
      '/api/v1/speaker-rag': {
        target: 'http://localhost:8012',
        changeOrigin: true,
        secure: false,
      },
      // Auth service
      '/api/v1/auth': {
        target: 'http://localhost:8011',
        changeOrigin: true,
        secure: false,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
  },
})
