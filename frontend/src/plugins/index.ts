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
axios.defaults.baseURL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'

// Configure axios interceptors for authentication
axios.interceptors.request.use(async (config) => {
  // Get token from localStorage
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`

    // Check if token is about to expire (last 5 minutes)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000
      const now = Date.now()

      // If token expires in less than 5 minutes, refresh it
      if (exp - now < 5 * 60 * 1000) {
        const response = await axios.post('/api/token/refresh', {
          token: token
        })
        const newToken = response.data.access_token
        localStorage.setItem('auth_token', newToken)
        config.headers.Authorization = `Bearer ${newToken}`
      }
    } catch (error) {
      // If refresh fails, redirect to login
      console.error('Token refresh failed:', error)
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }
  }
  return config
})

// Add response interceptor to handle 401 errors
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Clear auth state and redirect to login
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export function registerPlugins(app: App) {
  const pinia = createPinia()
  pinia.use(piniaPluginPersistedstate)

  app
    .use(vuetify)
    .use(pinia)
    .use(router)
}
