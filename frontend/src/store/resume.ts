import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
  }
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

export const useResumeStore = defineStore('resume', () => {
  const state = ref<GenerationState>({
    jobId: null,
    status: null,
    result: null,
    error: null,
    isPolling: false,
    pollInterval: null
  })

  const isGenerating = computed(() => 
    state.value.status && 
    !['idle', 'completed', 'failed'].includes(state.value.status.status)
  )

  const isCompleted = computed(() => 
    state.value.status?.status === 'completed'
  )

  const isFailed = computed(() => 
    state.value.status?.status === 'failed'
  )

  const progressPercentage = computed(() => 
    state.value.status?.progress || 0
  )

  const currentStep = computed(() => 
    state.value.status?.current_step || 'Initializing...'
  )

  const estimatedTimeRemaining = computed(() => 
    state.value.status?.estimated_time_remaining || null
  )

  const elapsedTime = computed(() => 
    state.value.status?.elapsed_time || 0
  )

  // Update axios interceptor for auth
  apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  async function startGeneration(
    jobDescription: File,
    skills?: string[],
    templateId?: string
  ): Promise<string> {
    try {
      clearState()
      
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

      state.value.jobId = response.data.job_id
      state.value.error = null
      
      // Start polling for status
      startPolling()
      
      return response.data.job_id
    } catch (error: any) {
      state.value.error = error.response?.data?.detail || 'Failed to start generation'
      throw error
    }
  }

  async function getStatus(jobId?: string): Promise<GenerationStatus | null> {
    try {
      const id = jobId || state.value.jobId
      if (!id) return null

      const response = await apiClient.get(`/generation-status/${id}`)
      state.value.status = response.data
      state.value.error = null
      
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        state.value.error = 'Generation job not found or expired'
        stopPolling()
      } else {
        state.value.error = error.response?.data?.detail || 'Failed to get status'
      }
      return null
    }
  }

  async function getResult(jobId?: string): Promise<GenerationResult | null> {
    try {
      const id = jobId || state.value.jobId
      if (!id) return null

      const response = await apiClient.get(`/generation-result/${id}`)
      state.value.result = response.data
      state.value.error = null
      
      return response.data
    } catch (error: any) {
      if (error.response?.status === 202) {
        // Still in progress, not an error
        return null
      } else if (error.response?.status === 404) {
        state.value.error = 'Generation result not found or expired'
      } else {
        state.value.error = error.response?.data?.detail || 'Failed to get result'
      }
      return null
    }
  }

  function startPolling() {
    if (state.value.isPolling) return

    state.value.isPolling = true
    state.value.pollInterval = window.setInterval(async () => {
      if (!state.value.jobId) {
        stopPolling()
        return
      }

      const status = await getStatus()
      if (!status) {
        stopPolling()
        return
      }

      // Check if generation is complete
      if (status.status === 'completed') {
        await getResult()
        stopPolling()
      } else if (status.status === 'failed') {
        stopPolling()
      }
    }, 2000) // Poll every 2 seconds
  }

  function stopPolling() {
    state.value.isPolling = false
    if (state.value.pollInterval) {
      clearInterval(state.value.pollInterval)
      state.value.pollInterval = null
    }
  }

  function clearState() {
    stopPolling()
    state.value.jobId = null
    state.value.status = null
    state.value.result = null
    state.value.error = null
  }

  function formatTime(seconds: number): string {
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
  }

  // Cleanup on store destruction
  function updateResumeContent(newContent: string) {
    if (state.value.result) {
      state.value.result.content = newContent
    }
  }

  function cleanup() {
    stopPolling()
  }

  return {
    // State
    state: computed(() => state.value),
    
    // Computed
    isGenerating,
    isCompleted,
    isFailed,
    progressPercentage,
    currentStep,
    estimatedTimeRemaining,
    elapsedTime,
    
    // Actions
    startGeneration,
    getStatus,
    getResult,
    startPolling,
    stopPolling,
    clearState,
    formatTime,
    cleanup,
    updateResumeContent
  }
})
