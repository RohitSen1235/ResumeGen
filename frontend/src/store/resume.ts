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
  company_name?: string // Added company_name
  job_title: string
  content: string
  agent_outputs: string
  analysis_summary?: string
  token_usage: any
  total_usage: any
  template_id?: string
  message: string
}

interface Template {
  id: string;
  name: string;
  description: string;
}

interface GenerationState {
  jobId: string | null
  status: GenerationStatus | null
  result: GenerationResult | null
  error: string | null
  isPolling: boolean
  pollInterval: number | null
  frontend_elapsed_time: number
  frontend_timer: number | null
  jobDescriptionText: string | null
  companyName: string | null
  jobTitle: string | null
  templates: Template[]
  templatesLastFetched: number | null
}

export const useResumeStore = defineStore('resume', {
  state: (): GenerationState => ({
    jobId: null,
    status: null,
    result: null,
    error: null,
    isPolling: false,
    pollInterval: null,
    frontend_elapsed_time: 0,
    frontend_timer: null,
    jobDescriptionText: null,
    companyName: null,
    jobTitle: null,
    templates: [],
    templatesLastFetched: null
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
    elapsedTime: (state) => state.frontend_elapsed_time || 0,
  },
  actions: {
    async startGeneration(
      jobDescription: File,
      companyName: string, // New parameter
      jobTitle: string,    // New parameter
      skills?: string[],
      templateId?: string
    ): Promise<string> {
      this.clearState()
      const startTime = Date.now()
      this.status = {
        status: 'idle',
        progress: 0,
        current_step: 'Initializing...',
        estimated_time_remaining: null,
        elapsed_time: 0,
        start_time: startTime
      }
      
      // Start frontend timer
      this.frontend_timer = window.setInterval(() => {
        this.frontend_elapsed_time = (Date.now() - startTime) / 1000
      }, 1000)
      
      try {
        const formData = new FormData()
        formData.append('job_description', jobDescription)
        formData.append('company_name', companyName) // Append companyName
        formData.append('job_title', jobTitle)       // Append jobTitle
        
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
        
        // Preserve start_time from the initial state
        const startTime = this.status?.start_time
        this.status = response.data
        if (startTime && this.status) {
          this.status.start_time = startTime
        }
        
        this.error = null
        
        // Keep frontend timer running independently - never stop it based on backend data
        // The frontend timer will only be stopped when generation completes or fails
        
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
      // Always clear any existing polling first
      this.stopPolling()

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
          this.stopFrontendTimer() // Stop timer only when generation completes
        } else if (status.status === 'failed') {
          this.stopPolling()
          this.stopFrontendTimer() // Stop timer only when generation fails
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
    
    stopFrontendTimer() {
      if (this.frontend_timer) {
        clearInterval(this.frontend_timer)
        this.frontend_timer = null
      }
    },
    clearState() {
      this.stopPolling()
      this.stopFrontendTimer()
      this.jobId = null
      this.status = null
      this.result = null
      this.error = null
      this.frontend_elapsed_time = 0
      this.jobDescriptionText = null
      this.companyName = null
      this.jobTitle = null
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
        await authStore.fetchCredits()
        console.log('Credits updated after resume generation')
      } catch (error) {
        console.error('Failed to update credits:', error)
      }
    },
    cleanup() {
      this.stopPolling()
    },
    
    restoreGenerationState() {
      // Check if there's an active generation that needs to be restored
      if (this.jobId && this.status && !['completed', 'failed'].includes(this.status.status)) {
        // Calculate the correct elapsed time since the job started
        const elapsedSeconds = (Date.now() - this.status.start_time) / 1000
        this.frontend_elapsed_time = elapsedSeconds
        
        // Restart the frontend timer
        this.stopFrontendTimer()
        this.frontend_timer = window.setInterval(() => {
          this.frontend_elapsed_time = (Date.now() - this.status!.start_time) / 1000
        }, 1000)
        
        // Restart polling to continue checking backend status
        this.startPolling()
        
        console.log('Restored generation state with elapsed time:', this.frontend_elapsed_time.toFixed(1) + 's')
      }
    },

    async fetchTemplates() {
      const now = Date.now();
      if (this.templates.length > 0 && this.templatesLastFetched && (now - this.templatesLastFetched < 300000)) { // 5 minute cache
        return;
      }

      try {
        const response = await apiClient.get('/templates');
        this.templates = response.data.templates;
        this.templatesLastFetched = now;
      } catch (error) {
        console.error('Failed to fetch templates:', error);
        // Optionally handle the error, e.g., by setting an error state
      }
    }
  }
})
