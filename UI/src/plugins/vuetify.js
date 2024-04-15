/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import { createVuetify } from 'vuetify'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
/**
 * vuetify configuration
 */
export default createVuetify({
  theme: {
		defaultTheme: "light",
    themes: {
			dark: false,
      light: {
        colors: {
          primary: '#151C55',
					secondary: '#84704C',
          white: '#f4f4f4',
					black: '#121314',
					quarternary: '#03DAC6',
					error: '#C31F1F',
					warning: '#FB8C00',
					success: '#106B13',
					info: '#2196F3',
        },
      },
    },
  },
})
