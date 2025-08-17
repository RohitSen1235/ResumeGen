import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'

export interface OnboardingData {
  fullName: string
  hasResume: boolean | null
  resumeFile: File | null
  resumePath: string | null
  parsedResumeData: any | null
  linkedinUrl: string
  portfolioUrl: string
  useResumeSections: boolean
  source: 'standard' | 'linkedin'
}

export const useOnboardingStore = defineStore('onboarding', () => {
  const auth = useAuthStore()
  
  // State
  const currentStep = ref(1)
  const totalSteps = ref(5)
  const loading = ref(false)
  const error = ref('')
  
  const data = ref<OnboardingData>({
    fullName: '',
    hasResume: null,
    resumeFile: null,
    resumePath: null,
    parsedResumeData: null,
    linkedinUrl: '',
    portfolioUrl: '',
    useResumeSections: false,
    source: 'standard'
  })

  // Computed
  const progress = computed(() => (currentStep.value / totalSteps.value) * 100)
  const canProceed = computed(() => {
    switch (currentStep.value) {
      case 1: // Name step
        return data.value.fullName.trim().length > 0
      case 2: // Resume step
        return data.value.hasResume !== null
      case 3: // LinkedIn step
        return true // Always optional
      case 4: // Portfolio step
        return true // Always optional
      case 5: // Preview step
        return true
      default:
        return false
    }
  })

  // Actions
  const nextStep = () => {
    if (currentStep.value < totalSteps.value && canProceed.value) {
      currentStep.value++
    }
  }

  const prevStep = () => {
    if (currentStep.value > 1) {
      currentStep.value--
    }
  }

  const setStep = (step: number) => {
    if (step >= 1 && step <= totalSteps.value) {
      currentStep.value = step
    }
  }

  const updateData = (updates: Partial<OnboardingData>) => {
    data.value = { ...data.value, ...updates }
  }

  const uploadResume = async (file: File) => {
    try {
      loading.value = true
      error.value = ''
      
      // First, ensure user has a basic profile for resume upload
      if (!auth.hasProfile) {
        const basicProfileData = {
          name: auth.user?.email?.split('@')[0] || 'User',
          linkedin_url: '',
          portfolio_url: '',
          resume_path: '',
          use_resume_sections: false,
          professional_title: '',
          summary: '',
          phone: '',
          location: '',
          github_url: ''
        }
        
        await auth.createProfile(basicProfileData)
        await auth.fetchUser()
      }
      
      const formData = new FormData()
      formData.append('resume', file)
      
      const response = await axios.post('/api/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${auth.token}`
        }
      })

      if (response.status === 200 && response.data) {
        updateData({
          resumeFile: file,
          resumePath: response.data.file_path || response.data.path,
          parsedResumeData: response.data.parsed_data || null,
          useResumeSections: true
        })
        return response.data
      }
    } catch (err: any) {
      error.value = 'Failed to upload resume: ' + (err.response?.data?.detail || err.message)
      throw err
    } finally {
      loading.value = false
    }
  }

  const completeOnboarding = async () => {
    try {
      loading.value = true
      error.value = ''

      // Update profile with onboarding data
      const profileData = {
        name: data.value.fullName || auth.user?.profile?.name || auth.user?.email?.split('@')[0] || 'User',
        linkedin_url: data.value.linkedinUrl,
        portfolio_url: data.value.portfolioUrl,
        resume_path: data.value.resumePath || undefined,
        use_resume_sections: data.value.useResumeSections,
        professional_title: auth.user?.profile?.professional_title || '',
        summary: auth.user?.profile?.summary || '',
        phone: auth.user?.profile?.phone || '',
        location: auth.user?.profile?.location || '',
        github_url: auth.user?.profile?.github_url || ''
      }

      // Create or update profile
      if (auth.hasProfile) {
        await auth.updateProfile(profileData)
      } else {
        await auth.createProfile(profileData)
      }

      // If we have parsed resume data, import the sections
      if (data.value.parsedResumeData && data.value.useResumeSections) {
        await importResumeData()
      }

      // Refresh user data
      await auth.fetchUser()
      
      // Mark onboarding as completed
      auth.markOnboardingCompleted()
      
      return true
    } catch (err: any) {
      error.value = 'Failed to complete onboarding: ' + (err.response?.data?.detail || err.message)
      throw err
    } finally {
      loading.value = false
    }
  }

  const importResumeData = async () => {
    if (!data.value.parsedResumeData) return

    try {
      const apiClient = axios.create({
        baseURL: import.meta.env.VITE_BACKEND_URL
      })

      apiClient.interceptors.request.use((config) => {
        const token = auth.token
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      })

      // Transform parsed data to match our API format
      const transformedData = transformParsedData(data.value.parsedResumeData)
      
      // Import sections
      await apiClient.post('/api/import-resume-sections', transformedData)
    } catch (err: any) {
      console.error('Failed to import resume sections:', err)
      // Don't throw here as profile creation should still succeed
    }
  }

  const transformParsedData = (parsedData: any) => {
    // Transform the parsed resume data to match our section format
    return {
      work_experience: parsedData.past_experiences?.map((exp: string, index: number) => ({
        position: `Position ${index + 1}`,
        company: 'Company Name',
        description: exp,
        start_date: null,
        end_date: null,
        current_job: false
      })) || [],
      education: parsedData.education?.map((edu: string, index: number) => ({
        institution: 'Institution',
        degree: edu,
        field_of_study: '',
        start_date: null,
        end_date: null
      })) || [],
      skills: parsedData.skills?.map((skill: string) => ({
        name: skill,
        category: 'General',
        proficiency: 'Intermediate'
      })) || [],
      projects: parsedData.Projects?.map((project: string, index: number) => ({
        name: `Project ${index + 1}`,
        description: project,
        start_date: null,
        end_date: null
      })) || []
    }
  }

  const reset = () => {
    currentStep.value = 1
    loading.value = false
    error.value = ''
    data.value = {
      fullName: '',
      hasResume: null,
      resumeFile: null,
      resumePath: null,
      parsedResumeData: null,
      linkedinUrl: '',
      portfolioUrl: '',
      useResumeSections: false,
      source: 'standard'
    }
  }

  return {
    // State
    currentStep,
    totalSteps,
    loading,
    error,
    data,
    
    // Computed
    progress,
    canProceed,
    
    // Actions
    nextStep,
    prevStep,
    setStep,
    updateData,
    uploadResume,
    completeOnboarding,
    reset
  }
})
