/**
 * plugins/index.ts
 *
 * Automatically included in `./src/main.ts`
 */

// Plugins
import vuetify from './vuetify'
import router from '../router'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import type { App } from 'vue'
import axios from 'axios'

// Configure axios base URL
// axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api'

export function registerPlugins(app: App) {
  const pinia = createPinia()
  pinia.use(piniaPluginPersistedstate)

  app
    .use(vuetify)
    .use(pinia)
    .use(router)
}
