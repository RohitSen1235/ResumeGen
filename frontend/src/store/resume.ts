import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './auth'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  }
})

// Update axios interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

interface GenerationStatus {
  status: 'idle' | 'parsing' | 'analyzing' | 'optimizing' | 'constructing' | 'completed' | 'failed'
  progress: number
  current_step: string
  estimated_time_remaining: number | null
  elapsed_time: number
  start_time: number
}

interface GenerationResult {
  job_id: string
  job_title: string
  content: string
  agent_outputs: string
  analysis_summary?: string
  token_usage: any
  total_usage: any
  template_id?: string
  message: string
}

interface GenerationState {
  jobId: string | null
  status: GenerationStatus | null
  result: GenerationResult | null
  error: string | null
  isPolling: boolean
  pollInterval: number | null
}

export const useResumeStore = defineStore('resume', {
  state: (): GenerationState => ({
    jobId: null,
    status: null,
    result: null,
    error: null,
    isPolling: false,
    pollInterval: null
  }),
  persist: true,
  getters: {
    isGenerating: (state): boolean => {
      return !!(state.status && !['idle', 'completed', 'failed'].includes(state.status.status));
    },
    isCompleted: (state) => state.status?.status === 'completed',
    isFailed: (state) => state.status?.status === 'failed',
    progressPercentage: (state) => state.status?.progress || 0,
    currentStep: (state) => state.status?.current_step || 'Initializing...',
    estimatedTimeRemaining: (state) => state.status?.estimated_time_remaining || null,
    elapsedTime: (state) => state.status?.elapsed_time || 0,
  },
  actions: {
    async startGeneration(
      jobDescription: File,
      skills?: string[],
      templateId?: string
    ): Promise<string> {
      try {
        this.clearState()
        
        const formData = new FormData()
        formData.append('job_description', jobDescription)
        
        if (skills && skills.length > 0) {
          skills.forEach(skill => formData.append('skills', skill))
        }
        
        if (templateId) {
          formData.append('template_id', templateId)
        }

        const response = await apiClient.post('/start-generation', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        this.jobId = response.data.job_id
        this.error = null
        
        // Start polling for status
        this.startPolling()
        
        return response.data.job_id
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Failed to start generation'
        throw error
      }
    },
    async getStatus(jobId?: string): Promise<GenerationStatus | null> {
      try {
        const id = jobId || this.jobId
        if (!id) return null

        const response = await apiClient.get(`/generation-status/${id}`)
        this.status = response.data
        this.error = null
        
        return response.data
      } catch (error: any) {
        if (error.response?.status === 404) {
          this.error = 'Generation job not found or expired'
          this.stopPolling()
        } else {
          this.error = error.response?.data?.detail || 'Failed to get status'
        }
        return null
      }
    },
    async getResult(jobId?: string): Promise<GenerationResult | null> {
      try {
        const id = jobId || this.jobId
        if (!id) return null

        const response = await apiClient.get(`/generation-result/${id}`)
        this.result = response.data
        this.error = null
        
        return response.data
      } catch (error: any) {
        if (error.response?.status === 202) {
          // Still in progress, not an error
          return null
        } else if (error.response?.status === 404) {
          this.error = 'Generation result not found or expired'
        } else {
          this.error = error.response?.data?.detail || 'Failed to get result'
        }
        return null
      }
    },
    startPolling() {
      if (this.isPolling) return

      this.isPolling = true
      this.pollInterval = window.setInterval(async () => {
        if (!this.jobId) {
          this.stopPolling()
          return
        }

        const status = await this.getStatus()
        if (!status) {
          this.stopPolling()
          return
        }

        // Check if generation is complete
        if (status.status === 'completed') {
          const result = await this.getResult()
          if (result) {
            await this.updateCredits()
          }
          this.stopPolling()
        } else if (status.status === 'failed') {
          this.stopPolling()
        }
      }, 2000) // Poll every 2 seconds
    },
    stopPolling() {
      this.isPolling = false
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
    clearState() {
      this.stopPolling()
      this.jobId = null
      this.status = null
      this.result = null
      this.error = null
    },
    formatTime(seconds: number): string {
      if (seconds < 60) {
        return `${Math.round(seconds)}s`
      } else if (seconds < 3600) {
        const minutes = Math.floor(seconds / 60)
        const remainingSeconds = Math.round(seconds % 60)
        return `${minutes}m ${remainingSeconds}s`
      } else {
        const hours = Math.floor(seconds / 3600)
        const minutes = Math.floor((seconds % 3600) / 60)
        return `${hours}h ${minutes}m`
      }
    },
    async updateResumeContent(newContent: string, resumeId?: string) {
      if (!this.result && !resumeId) return
      
      if (this.result) {
        this.result.content = newContent
      }
      
      try {
        const idToUpdate = resumeId || this.jobId
        if (idToUpdate) {
          await apiClient.put(`/resume/${idToUpdate}`, {
            content: newContent
          })
        }
      } catch (error) {
        console.error('Error saving resume content:', error)
        throw error
      }
    },
    async updateCredits() {
      try {
        // Refresh user data to get the latest credits from database
        const authStore = useAuthStore()
        await authStore.fetchUser()
        console.log('Credits updated after resume generation')
      } catch (error) {
        console.error('Failed to update credits:', error)
      }
    },
    cleanup() {
      this.stopPolling()
    }
  }
})
