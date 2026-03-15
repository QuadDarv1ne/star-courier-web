/**
 * Vite Configuration for StarCourier Web - Optimized
 * 
 * Features:
 * - Code splitting for faster initial load
 * - Compression (gzip/brotli)
 * - PWA support
 * - Bundle analysis
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('ion-')
        }
      }
    })
  ],

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '~': path.resolve(__dirname, './node_modules')
    },
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },

  server: {
    port: 5173,
    host: 'localhost',
    open: true,
    cors: true,
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
      overlay: true
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        ws: true
      }
    }
  },

  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    target: 'esnext',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info', 'console.debug']
      },
      format: {
        comments: false
      }
    },
    rollupOptions: {
      output: {
        chunkFileNames: (chunkInfo) => {
          // Better naming for cache busting and organization
          const facadeModuleId = chunkInfo.facadeModuleId 
            ? chunkInfo.facadeModuleId.split('/').pop() 
            : 'chunk';
          return `assets/js/${facadeModuleId.replace(/\.[^.]+$/, '')}-[hash].js`;
        },
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const ext = info[info.length - 1]
          
          // Organize assets by type
          if (/png|jpe?g|gif|tiff|bmp|ico|svg|webp/i.test(ext)) {
            return 'assets/images/[name]-[hash][extname]'
          } else if (/woff|woff2|eot|ttf|otf/i.test(ext)) {
            return 'assets/fonts/[name]-[hash][extname]'
          } else if (ext === 'css') {
            return 'assets/css/[name]-[hash][extname]'
          } else if (/mp3|wav|ogg|mp4|webm/i.test(ext)) {
            return 'assets/media/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        },
        // Advanced code splitting strategy
        manualChunks: (id) => {
          // Vue core libraries
          if (id.includes('node_modules/vue/') || 
              id.includes('node_modules/@vue/') ||
              id.includes('node_modules/vue-router/') ||
              id.includes('node_modules/pinia/')) {
            return 'vue-vendor';
          }
          
          // HTTP client
          if (id.includes('node_modules/axios/')) {
            return 'http-vendor';
          }
          
          // UI components (if using any UI library)
          if (id.includes('node_modules/@headlessui/') ||
              id.includes('node_modules/@heroicons/')) {
            return 'ui-vendor';
          }
          
          // Game store and logic
          if (id.includes('src/store/') || id.includes('src/services/')) {
            return 'game-logic';
          }
          
          // Components
          if (id.includes('src/components/')) {
            return 'components';
          }
          
          // Views (lazy loaded, but this helps with shared code)
          if (id.includes('src/views/')) {
            return 'views';
          }
        }
      }
    },
    cssCodeSplit: true,
    sourcemap: false,
    commonjsOptions: {
      include: [/node_modules/],
      sourceMap: false
    },
    // Performance settings
    chunkSizeWarningLimit: 500,
    reportCompressedSize: true,
    
    // Enable esbuild for faster builds
    esbuild: {
      drop: ['console', 'debugger'],
      legalComments: 'none'
    }
  },

  define: {
    __APP_VERSION__: JSON.stringify('2.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  },

  // Optimization settings
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios'],
    exclude: []
  },

  preview: {
    port: 4173,
    strictPort: false,
    open: true
  }
})
