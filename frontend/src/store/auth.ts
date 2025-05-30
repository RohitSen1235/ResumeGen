import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

interface Profile {
  id: number
  user_id: number
  name: string
  phone?: string
  location?: string
  linkedin_url?: string
  resume_path?: string
  professional_info?: any
  created_at: string
  updated_at?: string
}

interface User {
  id: number
  email: string
  profile: Profile | null
  created_at: string
  updated_at?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  // Initialize user data if token exists
  if (token.value) {
    fetchUser().catch(() => {
      // If fetching user fails, token might be expired
      logout()
    })
  }

  async function validateToken() {
    if (!token.value) return false
    try {
      await fetchUser()
      return true
    } catch {
      return false
    }
  }
  const hasProfile = computed(() => !!user.value?.profile)

  // Initialize axios interceptors for auth
  axios.interceptors.request.use(async (config) => {
    if (token.value) {
      // Add current token to request
      config.headers.Authorization = `Bearer ${token.value}`
      
      // Check if token is about to expire (last 5 minutes)
      try {
        const payload = JSON.parse(atob(token.value.split('.')[1]))
        const exp = payload.exp * 1000
        const now = Date.now()
        
        // If token expires in less than 5 minutes, refresh it
        if (exp - now < 5 * 60 * 1000) {
          const response = await axios.post('/api/token/refresh', {
            token: token.value
          })
          token.value = response.data.access_token
          localStorage.setItem('auth_token', response.data.access_token)
          config.headers.Authorization = `Bearer ${response.data.access_token}`
        }
      } catch (error) {
        // If refresh fails, logout user
        logout()
        throw error
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
        logout()
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }
  )

  async function login(email: string, password: string) {
    try {
      loading.value = true
      error.value = null

      const formData = new FormData()
      formData.append('username', email)
      formData.append('password', password)

      const response = await axios.post('/api/token', formData)
      token.value = response.data.access_token
      localStorage.setItem('auth_token', response.data.access_token)

      // After getting token, fetch user profile
      await fetchUser()
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function signup(email: string, password: string) {
    try {
      loading.value = true
      error.value = null

      const response = await axios.post('/api/signup', {
        email,
        password
      })
      user.value = response.data

      // After signup, login automatically
      await login(email, password)
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Signup failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function forgotPassword(email: string) {
    try {
      loading.value = true
      error.value = null
      
      await axios.post('/api/forgot-password', { email })
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to send password reset email'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function verifyResetToken(token: string): Promise<string> {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.get('/api/reset-password', {
        params: { token }
      })
      return response.data.email
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Invalid or expired token'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function resetPassword(token: string, password: string) {
    try {
      loading.value = true
      error.value = null
      
      const response = await axios.post('/api/reset-password', {
        token,
        new_password: password
      })
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to reset password'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      loading.value = true
      error.value = null

      // First get user data from token
      const userResponse = await axios.get('/api/user')
      user.value = userResponse.data

      // Then try to get profile
      try {
        const profileResponse = await axios.get('/api/profile')
        if (user.value) {
          user.value = {
            ...user.value,
            profile: profileResponse.data
          }
        }
      } catch (err: any) {
        if (err.response?.status !== 404) {
          throw err
        }
        // Explicitly set profile to null if 404
        if (user.value) {
          user.value = {
            ...user.value,
            profile: null
          }
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch user data'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function createProfile(profileData: Omit<Profile, 'id' | 'user_id' | 'created_at' | 'updated_at'>) {
    try {
      loading.value = true
      error.value = null

      const response = await axios.post('/api/profile', profileData)
      if (user.value) {
        user.value = {
          ...user.value,
          profile: response.data
        }
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create profile'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(profileData: Partial<Omit<Profile, 'id' | 'user_id' | 'created_at' | 'updated_at'>>) {
    try {
      loading.value = true
      error.value = null

      const response = await axios.put('/api/profile', profileData)
      if (user.value) {
        user.value = {
          ...user.value,
          profile: response.data
        }
      }
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update profile'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('auth_token')
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    hasProfile,
    login,
    signup,
    forgotPassword,
    verifyResetToken,
    resetPassword,
    fetchUser,
    createProfile,
    updateProfile,
    logout,
    validateToken
  }
})
