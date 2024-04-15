import './assets/main.css'
import 'nprogress/nprogress.css'
import { createApp } from 'vue'
import { createPinia } from "pinia"
import {
  // named imports because their names are too generic
  plugin as FormKitPlugin,
  defaultConfig as FormKitDefaultConfig
} from "@formkit/vue"

// Page stuff
import App from './App.vue'
import router from "@/router"

// Plugins
import { loadFonts } from "./plugins/webfontloader"
import vuetify from "./plugins/vuetify"
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import VueApexCharts from "vue3-apexcharts";

// setting up pinia
const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// registering the various plugins
loadFonts()
createApp(App)
	.use(pinia)
	.use(router)
	.use(FormKitPlugin, FormKitDefaultConfig({theme: "genesis"}))
	.use(vuetify)
	.use(VueApexCharts)
	.mount('#app')
