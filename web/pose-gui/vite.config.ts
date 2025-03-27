import { fileURLToPath, URL } from 'node:url';

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0',
    open: true,
    port: 8080,
    proxy: {
      '/api/': {
        target: 'http://localhost:8000/',
        ws: true,
        changeOrigin: true,
        secure: false,
      },
    },
  },
  plugins: [
    vue({
      template: {
        compilerOptions: {
          // i am ignorning my custom '<container>' tag
          isCustomElement: tag =>
            [
              'TresPerspectiveCamera',
              'TresTorusGeometry',
              'TresMeshBasicMaterial',
              'TresAmbientLight',
              'TresMesh',
              'TresMeshNormalMaterial',
              'TresBoxGeometry',
              'TresGroup',
            ].includes(tag),
        },
      },
    }),
    vueJsx(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  optimizeDeps: {
    include: [
      '@/assets/swagger-ui/swagger-ui-es-bundle.js',
      '@/assets/swagger-ui/swagger-ui-standalone-preset.js',
    ],
  },
  build: {
    commonjsOptions: {
      include: [
        /assets\/swagger-ui\/swagger-ui-es-bundle.js$/,
        /assets\/swagger-ui\/swagger-ui-standalone-preset.js$/,
      ],
    },
  },
});
