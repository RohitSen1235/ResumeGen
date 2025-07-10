/**
 * plugins/index.ts
 *
 * Automatically included in `./src/main.ts`
 */

// Plugins
import vuetify from './vuetify'
import router from '../router'
import { createPinia } from 'pinia'
import type { App } from 'vue'
import axios from 'axios'

// Configure axios base URL
axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api'

export function registerPlugins(app: App) {
  app
    .use(vuetify)
    .use(createPinia())
    .use(router)
}
