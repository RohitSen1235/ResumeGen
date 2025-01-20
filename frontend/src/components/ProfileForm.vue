<template>
  <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="800">
    <v-card-title class="text-h5 mb-4">
      <v-icon icon="mdi-account-circle" size="large" class="mr-2" color="primary"></v-icon>
      Profile Information
    </v-card-title>

    <v-card-subtitle class="mb-4">
      Complete your profile to use the resume builder
    </v-card-subtitle>

    <v-alert
      v-if="!auth.isAuthenticated"
      type="warning"
      variant="tonal"
      class="mb-4"
      icon="mdi-alert-circle"
    >
      Please login to access your profile
    </v-alert>

    <v-form v-else @submit.prevent="handleSubmit" v-model="isValid">
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field
            v-model="profileData.name"
            label="Full Name *"
            :rules="[v => !!v || 'Name is required']"
            variant="outlined"
            density="comfortable"
          ></v-text-field>
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            v-model="profileData.phone"
            label="Phone Number"
            variant="outlined"
            density="comfortable"
            placeholder="Optional"
          ></v-text-field>
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            v-model="profileData.location"
            label="Location"
            variant="outlined"
            density="comfortable"
            placeholder="Optional"
          ></v-text-field>
        </v-col>

        <v-col cols="12" md="6">
          <v-text-field
            v-model="profileData.linkedin_url"
            label="LinkedIn Profile URL"
            variant="outlined"
            density="comfortable"
            placeholder="Optional"
            :rules="[
              v => !v || v.includes('linkedin.com/in/') || 'Please enter a valid LinkedIn profile URL'
            ]"
          ></v-text-field>
        </v-col>

        <v-col cols="12">
          <!-- Show current resume if exists -->
          <!-- Current Resume -->
          <v-alert
            v-if="profileData.resume_path"
            color="info"
            variant="tonal"
            class="mb-4"
            icon="mdi-file-pdf-box"
            border="start"
          >
            <div class="d-flex align-center justify-space-between">
              <div class="d-flex align-center">
                <span class="mr-2">Current Resume:</span>
                <span class="font-weight-medium">{{ getResumeFileName() }}</span>
              </div>
              <div class="d-flex align-center">
                <v-btn
                  color="primary"
                  variant="text"
                  size="small"
                  :href="`/api/resume/${getResumeFileName()}`"
                  target="_blank"
                  prepend-icon="mdi-open-in-new"
                  class="mr-2"
                >
                  View Resume
                </v-btn>
                <v-btn
                  color="error"
                  variant="text"
                  size="small"
                  @click="handleDeleteResume"
                  prepend-icon="mdi-delete"
                  :loading="deleteLoading"
                >
                  Delete
                </v-btn>
              </div>
            </div>
          </v-alert>

          <v-file-input
            v-model="resumeFile"
            label="Upload Resume (PDF)"
            accept=".pdf"
            variant="outlined"
            density="comfortable"
            placeholder="Optional"
            prepend-icon="mdi-file-pdf-box"
            :hint="profileData.resume_path ? 'Upload a new resume to replace the current one' : 'This will be used as a reference for generating new resumes'"
            persistent-hint
          ></v-file-input>
        </v-col>
      </v-row>

      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        class="my-4"
        closable
      >
        {{ error }}
      </v-alert>

      <div class="d-flex justify-end mt-6">
        <v-btn
          type="submit"
          color="primary"
          size="large"
          :loading="loading"
          :disabled="!isValid"
        >
          {{ auth.hasProfile ? 'Update Profile' : 'Create Profile' }}
        </v-btn>
      </div>
                <!-- Resume History Section -->
                <v-card class="mb-4 mt-8" variant="outlined">
            <v-card-title class="text-h6 font-weight-medium">
              <v-icon icon="mdi-history" class="mr-2"></v-icon>
              Previously Generated Resume
            </v-card-title>
            
            <v-card-text>
              <v-list>
                <v-list-item
                  v-for="resume in resumeHistory"
                  :key="resume.id"
                  class="px-0"
                >
                  <template v-slot:prepend>
                    <v-icon icon="mdi-file-pdf-box" color="primary"></v-icon>
                  </template>

                  <v-list-item-title class="font-weight-medium">
                    {{ resume.name }}
                  </v-list-item-title>
                  <v-list-item-subtitle>
                    {{ new Date(resume.created_at).toLocaleDateString() }}
                  </v-list-item-subtitle>

                  <template v-slot:append>
                    <v-btn
                      color="primary"
                      variant="text"
                      size="small"
                      :href="`/api/resume/${resume.id}`"
                      target="_blank"
                      prepend-icon="mdi-open-in-new"
                      class="mr-2"
                    >
                      View
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

    </v-form>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

const auth = useAuthStore()
const router = useRouter()

interface ResumeHistoryItem {
  id: string
  name: string
  created_at: string
}

const profileData = ref({
  name: '',
  phone: '',
  location: '',
  linkedin_url: '',
  resume_path: ''
})

const resumeHistory = ref<ResumeHistoryItem[]>([])
const resumeFile = ref<File | null>(null)
const isValid = ref(false)
const error = ref('')
const loading = ref(false)
const deleteLoading = ref(false)

const handleDeleteResume = async () => {
  try {
    deleteLoading.value = true
    await axios.delete('/api/delete-resume')
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
    const response = await axios.get<ResumeHistoryItem[]>('/api/resumes')
    resumeHistory.value = response.data
  } catch (error) {
    console.error('Failed to fetch resume history:', error)
  }
}

onMounted(async () => {
  if (auth.user?.profile) {
    const { name, phone, location, linkedin_url, resume_path } = auth.user.profile
    profileData.value = {
      name: name || '',
      phone: phone || '',
      location: location || '',
      linkedin_url: linkedin_url || '',
      resume_path: resume_path || ''
    }
    await fetchResumeHistory()
  }
})

const getResumeFileName = () => {
  if (!profileData.value.resume_path) return ''
  return profileData.value.resume_path.split('/').pop()
}

const handleSubmit = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    const data = { ...profileData.value }
    
    // Handle resume file upload if provided
    if (resumeFile.value) {
      const formData = new FormData()
      formData.append('resume', resumeFile.value)
      
      // Use axios instead of fetch for automatic token handling
      const response = await axios.post('/api/upload-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
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
