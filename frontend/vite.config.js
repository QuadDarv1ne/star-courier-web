/**
 * Vite Configuration for StarCourier Web
 * Build configuration for Vue.js frontend
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  // ============================================================================
  // PLUGINS
  // ============================================================================

  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('ion-')
        }
      }
    })
  ],

  // ============================================================================
  // RESOLVE
  // ============================================================================

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~': path.resolve(__dirname, './node_modules')
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },

  // ============================================================================
  // DEV SERVER
  // ============================================================================

  server: {
    port: 5173,
    host: 'localhost',
    open: true,
    cors: true,
    
    // HMR Configuration
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
      overlay: true
    },

    // Proxy API requests to backend
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        ws: true
      }
    }
  },

  // ============================================================================
  // BUILD
  // ============================================================================

  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    target: 'esnext',
    minify: 'terser',
    
    // Rollup options
    rollupOptions: {
      output: {
        // Chunk file names
        chunkFileNames: 'assets/[name]-[hash].js',
        // Entry file names
        entryFileNames: 'assets/[name]-[hash].js',
        // Asset file names
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          
          if (/png|jpe?g|gif|tiff|bmp|ico/i.test(ext)) {
            return `assets/images/[name]-[hash][extname]`
          } else if (/woff|woff2|eot|ttf|otf/i.test(ext)) {
            return `assets/fonts/[name]-[hash][extname]`
          } else if (ext === 'css') {
            return `assets/css/[name]-[hash][extname]`
          }
          
          return `assets/[name]-[hash][extname]`
        }
      }
    },

    // CSS code split
    cssCodeSplit: true,

    // Source maps
    sourcemap: false, // Set to true for development

    // Optimization
    commonjsOptions: {
      include: [/node_modules/],
      sourceMap: false
    }
  },

  // ============================================================================
  // ENVIRONMENT VARIABLES
  // ============================================================================

  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  },

  // ============================================================================
  // CSS OPTIONS
  // ============================================================================

  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
          $primary: #fbbf24;
          $secondary: #ea580c;
          $dark: #0f172a;
        `
      }
    }
  },

  // ============================================================================
  // PREVIEW (for testing production build locally)
  // ============================================================================

  preview: {
    port: 4173,
    strictPort: false,
    open: true
  }
})
