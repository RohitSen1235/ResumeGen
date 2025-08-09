import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  }
})

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
  is_admin: boolean
  credits: number
  profile: Profile | null
  created_at: string
  updated_at?: string
  userType?: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(JSON.parse(localStorage.getItem('auth_user') || 'null'))
  const token = ref<string | null>(localStorage.getItem('auth_token'))
  const loading = ref(false)
  const error = ref<string | null>(null)
  const initializing = ref(!!token.value)

  const isAuthenticated = computed(() => !!token.value)

  // Initialize auth state
  if (token.value) {
    fetchUser()
      .then(() => {
        // Store user data in localStorage
        if (user.value) {
          localStorage.setItem('auth_user', JSON.stringify({
            id: user.value.id,
            email: user.value.email,
            credits: user.value.credits,
            created_at: user.value.created_at
          }))
          localStorage.setItem('auth_user', JSON.stringify({
            id: user.value.id,
            email: user.value.email,
            credits: user.value.credits,
            created_at: user.value.created_at
          }))
        }
      })
      .catch(() => logout())
      .finally(() => initializing.value = false)
  }

  async function validateToken() {
    if (!token.value) {
      // console.log('validateToken: No token available')
      return false
    }
    try {
      // console.log('validateToken: Validating token...')
      await fetchUser()
      // console.log('validateToken: Token is valid')
      return true
    } catch (error) {
      console.error('validateToken: Token validation failed:', error)
      return false
    }
  }
  const hasProfile = computed(() => !!user.value?.profile)
  const isAdmin = computed(() => user.value?.is_admin || false)

  // Initialize axios interceptors for auth
  apiClient.interceptors.request.use(async (config) => {
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
  apiClient.interceptors.response.use(
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

      const response = await apiClient.post('/token', formData)
      token.value = response.data.access_token
      localStorage.setItem('auth_token', response.data.access_token)
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`

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

      const response = await apiClient.post('/signup', {
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
      
      await apiClient.post('/forgot-password', { email })
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
      
      const response = await apiClient.get('/reset-password', {
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
      
      const response = await apiClient.post('/reset-password', {
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

  async function linkedinLogin() {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiClient.get('/auth/linkedin')
      const { auth_url } = response.data
      
      // Redirect to LinkedIn OAuth
      window.location.href = auth_url
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'LinkedIn login failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function handleLinkedinCallback(code: string, state: string) {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiClient.get(`/auth/linkedin/callback?code=${code}&state=${state}`)
      const { access_token, user: userData } = response.data
      
      token.value = access_token
      user.value = userData
      localStorage.setItem('auth_token', access_token)
      localStorage.setItem('auth_user', JSON.stringify(userData))
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return userData
    } catch (err: any) {
      console.error('LinkedIn callback error details:', err.response?.data)
      error.value = err.response?.data?.detail || 'LinkedIn authentication failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  async function fetchUser() {
    try {
      loading.value = true
      error.value = null
      console.log('fetchUser: Attempting to fetch user data')

      // First get user data from token
      const userResponse = await apiClient.get('/user')
      console.log('fetchUser: Successfully fetched user data')
      user.value = {
        ...userResponse.data,
        is_admin: userResponse.data.is_admin || false
      }

      // Then try to get profile
      try {
        const profileResponse = await apiClient.get('/profile')
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

      const response = await apiClient.post('/profile', profileData)
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

      const response = await apiClient.put('/profile', profileData)
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
    localStorage.removeItem('auth_user')
    delete apiClient.defaults.headers.common['Authorization']
  }

  function setUserType(type: string) {
    if (user.value) {
      user.value.userType = type
    }
  }

  function updateCredits(newCredits: number) {
    if (user.value) {
      user.value = {
        ...user.value,
        credits: newCredits
      }
      localStorage.setItem('auth_user', JSON.stringify({
        id: user.value.id,
        email: user.value.email,
        credits: newCredits,
        created_at: user.value.created_at
      }))
    }
  }

  return {
    user,
    token,
    loading,
    error,
    initializing,
    isAuthenticated,
    hasProfile,
    login,
    signup,
    forgotPassword,
    verifyResetToken,
    resetPassword,
    linkedinLogin,
    handleLinkedinCallback,
    fetchUser,
    createProfile,
    updateProfile,
    logout,
    validateToken,
    isAdmin,
    setUserType,
    updateCredits
  }
})
