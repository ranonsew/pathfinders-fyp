import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueRouter from "unplugin-vue-router/vite"
import vuetify, { transformAssetUrls } from "vite-plugin-vuetify";
import vueMarkdown from "unplugin-vue-markdown/vite"


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
		vueRouter({
			routesFolder: "src/views",
			extensions: [".vue", ".md"],
		}),
    vue({
      template: { transformAssetUrls },
			include: [/\.vue$/, /\.md$/],
    }),
		// https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vite-plugin
    vuetify({
      autoImport: true,
			styles: {
				configFile: "src/assets/settings.scss",
			},
    }),
		vueMarkdown({}),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
    extensions: [
			".js",
			".json",
			".jsx",
			".mjs",
			".ts",
			".tsx",
			".vue",
			".jpg",
			".png",
		],
  },
})
