<template>
  <v-container fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);" class="pa-4">
    <v-row>
      <!-- Left Column - Profile Fields -->
      <v-col cols="12" md="7">
        <v-card class="pa-md-8 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="text-h4 font-weight-bold mb-2 text-grey-darken-3">
            <v-icon icon="mdi-account-circle-outline" class="mr-3" color="primary"></v-icon>
            Profile Information
          </v-card-title>
          <v-card-subtitle class="text-body-1 mb-8 text-grey-darken-1">
            Complete your profile to unlock the full power of the resume builder.
          </v-card-subtitle>

          <v-form @submit.prevent="handleSubmit" v-model="isValid">
            <v-text-field
              v-model="profileData.name"
              label="Full Name *"
              :rules="[v => !!v || 'Name is required']"
              variant="outlined"
              density="comfortable"
              prepend-inner-icon="mdi-account-outline"
              class="mb-4"
            ></v-text-field>

            <v-text-field
              :model-value="auth.user?.email"
              label="Email"
              variant="outlined"
              density="comfortable"
              readonly
              disabled
              prepend-inner-icon="mdi-email-outline"
              class="mb-4"
            ></v-text-field>

            <v-text-field
              v-model="profileData.phone"
              label="Phone Number"
              variant="outlined"
              density="comfortable"
              placeholder="Optional"
              prepend-inner-icon="mdi-phone-outline"
              class="mb-4"
            ></v-text-field>

            <v-text-field
              v-model="profileData.location"
              label="Location"
              variant="outlined"
              density="comfortable"
              placeholder="Optional"
              prepend-inner-icon="mdi-map-marker-outline"
              class="mb-4"
            ></v-text-field>

            <v-text-field
              v-model="profileData.linkedin_url"
              label="LinkedIn Profile URL"
              variant="outlined"
              density="comfortable"
              placeholder="Optional"
              :rules="[v => !v || v.includes('linkedin.com/in/') || 'Please enter a valid LinkedIn profile URL']"
              prepend-inner-icon="mdi-linkedin"
              class="mb-6"
            ></v-text-field>

            <UserTypeSelector />
            <TypeRecommendations class="my-6" />

            <v-divider class="my-6"></v-divider>

            <div class="text-h6 mb-4 font-weight-medium">Existing Resume/CV</div>
            <v-radio-group v-model="hasExistingResume" inline>
              <v-radio label="Upload Existing Resume" :value="true"></v-radio>
              <v-radio label="Start Fresh" :value="false"></v-radio>
            </v-radio-group>

            <v-expand-transition>
              <div v-if="hasExistingResume" class="mt-4">
                <v-alert v-if="profileData.resume_path" color="success" variant="tonal" class="mb-4" icon="mdi-check-circle-outline" border="start">
                  <div class="d-flex align-center justify-space-between">
                    <div>
                      <span class="font-weight-medium">{{ getResumeFileName() }}</span> uploaded.
                    </div>
                    <div>
                      <v-btn color="primary" variant="text" size="small" :href="`/api/resume/${getResumeFileName()}`" target="_blank" prepend-icon="mdi-eye-outline">View</v-btn>
                      <v-btn color="error" variant="text" size="small" @click="handleDeleteResume" prepend-icon="mdi-delete-outline" :loading="deleteLoading">Delete</v-btn>
                    </div>
                  </div>
                </v-alert>

                <v-file-input
                  v-model="resumeFile"
                  label="Upload Resume (PDF)"
                  accept=".pdf"
                  prepend-icon=""
                  prepend-inner-icon="mdi-file-upload-outline"
                  variant="outlined"
                  density="comfortable"
                  :loading="uploadStatus === 'uploading'"
                  :error-messages="uploadStatus === 'error' ? 'Upload failed. Please try again.' : ''"
                  @change="handleResumeUpload"
                  clearable
                ></v-file-input>
                
                <v-card variant="outlined" class="mt-4 pa-4" rounded="lg">
                  <v-switch
                    v-model="useAsReference"
                    label="Use this resume as a reference"
                    color="primary"
                    inset
                    :disabled="!profileData.resume_path && !resumeFile"
                  ></v-switch>
                </v-card>
              </div>
            </v-expand-transition>

            <v-alert v-if="error" type="error" variant="tonal" class="my-6" closable>{{ error }}</v-alert>

            <div class="d-flex justify-end mt-8">
              <v-btn type="submit" color="primary" size="x-large" :loading="loading" :disabled="!isValid" rounded="lg" elevation="4">
                {{ auth.hasProfile ? 'Update Profile' : 'Create Profile' }}
              </v-btn>
            </div>
          </v-form>
        </v-card>
      </v-col>

      <!-- Right Column - Resume History -->
      <v-col cols="12" md="5">
        <v-card class="pa-md-6 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="text-h5 font-weight-bold mb-4 text-grey-darken-3">
            <v-icon icon="mdi-history" class="mr-3" color="primary"></v-icon>
            Resume History
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="resumeHistory.length" lines="two" class="bg-transparent">
              <v-list-item v-for="resume in resumeHistory" :key="resume.id" class="mb-2" border rounded="lg">
                <template v-slot:prepend>
                  <v-avatar color="primary" size="40">
                    <v-icon icon="mdi-file-document-outline" color="white"></v-icon>
                  </v-avatar>
                </template>
                <v-list-item-title class="font-weight-medium">{{ extractJobTitle(resume.role || resume.name || '') || 'Resume' }}</v-list-item-title>
                <v-list-item-subtitle>{{ formatDateWithTime(resume.created_at) }}</v-list-item-subtitle>
                <template v-slot:append>
                  <v-btn color="primary" variant="text" size="small" @click="$router.push(`/resume/${resume.id}`)" icon="mdi-arrow-right"></v-btn>
                </template>
              </v-list-item>
            </v-list>
            <v-alert v-else type="info" variant="tonal" class="text-center" icon="mdi-information-outline">
              You have no previously generated resumes.
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'
import UserTypeSelector from './UserTypeSelector.vue'
import TypeRecommendations from './TypeRecommendations.vue'

const auth = useAuthStore()
const router = useRouter()

interface ResumeHistoryItem {
  id: string
  name: string
  role?: string
  created_at: string
}

const profileData = ref({
  name: '',
  phone: '',
  location: '',
  linkedin_url: '',
  resume_path: '',
  use_resume_as_reference: true,
  userType: auth.user?.userType || ''
})

const resumeHistory = ref<ResumeHistoryItem[]>([])
const resumeFile = ref()
const hasExistingResume = ref(false)
const useAsReference = ref(true)
const isValid = ref(false)
const error = ref('')
const loading = ref(false)
const deleteLoading = ref(false)
const uploadStatus = ref<'idle' | 'uploading' | 'success' | 'error'>('idle')

// Watch for user type changes and update via API
watch(() => auth.user?.userType, (newType: string | undefined) => {
  if (newType) {
    profileData.value.userType = newType
    axios.post('/api/user-type', { user_type: newType }, {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    }).catch(err => {
      console.error('Failed to update user type:', err)
    })
  }
})

// Watch for changes in hasExistingResume to clear errors
watch(hasExistingResume, (newValue) => {
  if (!newValue) {
    // Reset upload state when user selects "No, I'll start fresh"
    resumeFile.value = null
    uploadStatus.value = 'idle'
    error.value = ''
  } else {
    // Clear errors when user selects "Yes, I want to upload one"
    error.value = ''
  }
})

// Watch for upload status changes to clear errors on success
watch(uploadStatus, (newStatus) => {
  if (newStatus === 'success') {
    error.value = ''
  }
})

// Watch for changes in useAsReference toggle to update profile data
watch(useAsReference, (newValue) => {
  profileData.value.use_resume_as_reference = newValue
})

const handleDeleteResume = async () => {
  try {
    deleteLoading.value = true
    await axios.delete('/api/delete-resume', {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    profileData.value.resume_path = ''
    await auth.fetchUser() // Refresh user data
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.toString()
  } finally {
    deleteLoading.value = false
  }
}

const fetchResumeHistory = async () => {
  try {
    const response = await axios.get<ResumeHistoryItem[]>('/api/resumes', {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    resumeHistory.value = response.data
  } catch (error) {
    console.error('Failed to fetch resume history:', error)
  }
}

onMounted(async () => {
  if (auth.user?.profile) {
    const profile = auth.user.profile
    profileData.value = {
      name: profile.name || '',
      phone: profile.phone || '',
      location: profile.location || '',
      linkedin_url: profile.linkedin_url || '',
      resume_path: profile.resume_path || '',
      use_resume_as_reference: (profile as any).use_resume_as_reference ?? true,
      userType: auth.user?.userType || ''
    }

    // Sync the useAsReference reactive variable with the profile data
    useAsReference.value = profileData.value.use_resume_as_reference

    // Auto-fill from LinkedIn data if available
    if (profile.linkedin_url && profile.professional_info?.linkedin_data) {
      const linkedinData = profile.professional_info.linkedin_data
      profileData.value = {
        ...profileData.value,
        name: linkedinData.name || profileData.value.name,
        // Can add more fields here if needed from linkedinData
      }
    }

    await fetchResumeHistory()
  }
})

const getResumeFileName = () => {
  if (!profileData.value.resume_path) return ''
  return profileData.value.resume_path.split('/').pop()
}

const handleResumeUpload = async () => {
  if (!resumeFile.value) {
    uploadStatus.value = 'idle'
    return
  }

  try {
    uploadStatus.value = 'uploading'
    // Clear any previous errors
    error.value = ''
    
    const formData = new FormData()
    formData.append('resume', resumeFile.value)
    
    // Upload the file using the correct endpoint
    const uploadResponse = await axios.post('/api/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${auth.token}`
      }
    })

    // Check if upload was successful
    if (uploadResponse.status === 200 && uploadResponse.data) {
      // Update profile data with the uploaded file path
      profileData.value = {
        ...profileData.value,
        resume_path: uploadResponse.data.file_path || uploadResponse.data.path
      }
      
      uploadStatus.value = 'success'
      await auth.fetchUser() // Refresh user data
    } else {
      throw new Error('Upload response was not successful')
    }
  } catch (err: any) {
    uploadStatus.value = 'error'
    console.error('Upload error:', err)
    error.value = 'Failed to upload resume: ' + (err.response?.data?.detail || err.message || 'Unknown error')
    resumeFile.value = null
  }
}

const formatDateWithTime = (dateString: string) => {
  const date = new Date(dateString)
  const dateOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }
  const timeOptions: Intl.DateTimeFormatOptions = {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  }
  
  const formattedDate = date.toLocaleDateString('en-GB', dateOptions)
  const formattedTime = date.toLocaleTimeString('en-GB', timeOptions)
  
  return `${formattedDate}@${formattedTime}`
}

const extractJobTitle = (resumeName: string) => {
  // Extract job title from formats like "Resume for id : fb48|quantitative-analytics-specialist"
  if (resumeName.includes('|')) {
    const jobTitle = resumeName.split('|')[1]
    if (jobTitle) {
      // Convert hyphenated job title to readable format
      return jobTitle.split('-').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
    }
  }
  return ''
}

const handleSubmit = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    const data = { 
      name: profileData.value.name,
      phone: profileData.value.phone,
      location: profileData.value.location,
      linkedin_url: profileData.value.linkedin_url,
      resume_path: profileData.value.resume_path,
      use_resume_as_reference: profileData.value.use_resume_as_reference,
      userType: auth.user?.userType || ''
    }
    
    // Handle resume file upload if provided
    if (resumeFile.value) {
      const formData = new FormData()
      formData.append('resume', resumeFile.value)
      
      // Use axios instead of fetch for automatic token handling
      const response = await axios.post('/api/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${auth.token}`
        }
      })
      data.resume_path = response.data.path
    }

    if (auth.hasProfile) {
      await auth.updateProfile(data)
    } else {
      await auth.createProfile(data)
    }

    // Fetch user profile again to ensure state is updated
    await auth.fetchUser()
    
    // Only navigate after confirming profile is updated
    if (auth.hasProfile) {
      router.push('/resume-builder')
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.toString()
  } finally {
    loading.value = false
  }
}
</script>
