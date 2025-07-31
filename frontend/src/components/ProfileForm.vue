<template>
  <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="1200">
    <v-card-title class="text-h5 mb-4">
      <v-icon icon="mdi-account-circle" size="large" class="mr-2" color="primary"></v-icon>
      Profile Information
    </v-card-title>

    <v-card-subtitle class="mb-4">
      Step 1 of 4: Complete your profile to use the resume builder
    </v-card-subtitle>

    <v-alert
      v-if="profileData.linkedin_url"
      type="info"
      variant="tonal"
      class="mb-4"
      icon="mdi-linkedin"
      border="start"
    >
      Profile imported from LinkedIn
    </v-alert>

    <!-- LinkedIn Data Section -->
    <v-expansion-panels v-if="profileData.linkedin_url && auth.user?.profile?.professional_info?.linkedin_data" class="mb-4">
      <v-expansion-panel>
        <v-expansion-panel-title>
          <v-icon icon="mdi-linkedin" class="mr-2" color="primary"></v-icon>
          LinkedIn Profile Details
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-card variant="flat" class="pa-4">
            <v-card-text>
              <div v-if="auth.user.profile.professional_info.linkedin_data.summary" class="mb-4">
                <div class="text-subtitle-1 font-weight-medium mb-2">Summary</div>
                <div class="text-body-1">{{ auth.user.profile.professional_info.linkedin_data.summary }}</div>
              </div>

              <div v-if="auth.user.profile.professional_info.linkedin_data.positions?.length" class="mb-4">
                <div class="text-subtitle-1 font-weight-medium mb-2">Experience</div>
                <v-list lines="two" density="comfortable">
                  <v-list-item
                    v-for="(position, i) in auth.user.profile.professional_info.linkedin_data.positions"
                    :key="i"
                    class="px-0"
                  >
                    <v-list-item-title class="font-weight-medium">
                      {{ position.title }} at {{ position.company }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      {{ position.duration }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle v-if="position.description">
                      {{ position.description }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </div>

              <div v-if="auth.user.profile.professional_info.linkedin_data.education?.length" class="mb-4">
                <div class="text-subtitle-1 font-weight-medium mb-2">Education</div>
                <v-list lines="two" density="comfortable">
                  <v-list-item
                    v-for="(edu, i) in auth.user.profile.professional_info.linkedin_data.education"
                    :key="i"
                    class="px-0"
                  >
                    <v-list-item-title class="font-weight-medium">
                      {{ edu.degree }} at {{ edu.school }}
                    </v-list-item-title>
                    <v-list-item-subtitle>
                      {{ edu.duration }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </div>

              <div v-if="auth.user.profile.professional_info.linkedin_data.skills?.length">
                <div class="text-subtitle-1 font-weight-medium mb-2">Skills</div>
                <v-chip-group>
                  <v-chip
                    v-for="(skill, i) in auth.user.profile.professional_info.linkedin_data.skills"
                    :key="i"
                    color="primary"
                    variant="outlined"
                    size="small"
                  >
                    {{ skill }}
                  </v-chip>
                </v-chip-group>
              </div>
            </v-card-text>
          </v-card>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>

    <v-alert
      v-if="!auth.isAuthenticated"
      type="warning"
      variant="tonal"
      class="mb-4"
      icon="mdi-alert-circle"
    >
      Please login to access your profile
    </v-alert>

    <v-row v-else>
      <!-- Left Column - Profile Fields -->
      <v-col cols="12" md="6">
        <v-form @submit.prevent="handleSubmit" v-model="isValid">
          <v-text-field
            v-model="profileData.name"
            label="Full Name *"
            :rules="[v => !!v || 'Name is required']"
            variant="outlined"
            density="comfortable"
            hint="Your full name as it should appear on your resume"
            persistent-hint
          ></v-text-field>

          <v-text-field
            :model-value="auth.user?.email"
            label="Email"
            variant="outlined"
            density="comfortable"
            readonly
            disabled
            hint="Your account email address"
            persistent-hint
          ></v-text-field>

          <v-text-field
            v-model="profileData.phone"
            label="Phone Number"
            variant="outlined"
            density="comfortable"
            placeholder="Optional"
            hint="Best contact number for potential employers"
            persistent-hint
          ></v-text-field>

          <v-text-field
            v-model="profileData.location"
            label="Location"
            variant="outlined"
            density="comfortable"
            placeholder="Optional"
            hint="City and country where you're based"
            persistent-hint
          ></v-text-field>

          <v-text-field
            v-model="profileData.linkedin_url"
            label="LinkedIn Profile URL"
            variant="outlined"
            density="comfortable"
            placeholder="Optional"
            :rules="[
              v => !v || v.includes('linkedin.com/in/') || 'Please enter a valid LinkedIn profile URL'
            ]"
            hint="We'll use this to auto-fill your experience and education"
            persistent-hint
          ></v-text-field>

          <UserTypeSelector />
          <TypeRecommendations class="mt-4" />

          <!-- Resume Upload Section -->
          <v-radio-group v-model="hasExistingResume" label="Do you have an existing resume/CV?" class="mb-2">
            <v-radio label="Yes, I want to upload one" value="yes"></v-radio>
            <v-radio label="No, I'll start fresh" value="no"></v-radio>
          </v-radio-group>

          <template v-if="hasExistingResume === 'yes'">
            <!-- Show current resume if exists -->
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
                  <span class="mr-2">Reference Resume:</span>
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
              label="Upload Reference Resume (PDF)"
              accept=".pdf"
              variant="outlined"
              density="comfortable"
              placeholder="Optional"
              prepend-icon="mdi-file-pdf-box"
              hint="Uploading a resume helps us suggest better content and formatting for your new resume"
              persistent-hint
              @change="handleResumeUpload"
            >
              <template v-slot:append-inner>
                <v-tooltip text="We'll parse your resume to auto-fill profile details" location="bottom">
                  <template v-slot:activator="{ props }">
                    <v-icon v-bind="props" icon="mdi-information-outline"></v-icon>
                  </template>
                </v-tooltip>
              </template>
            </v-file-input>

            <v-switch
              v-model="useAsReference"
              label="Use this resume as reference for generation"
              color="primary"
              inset
              class="mt-2"
              :disabled="!profileData.resume_path && !resumeFile.value"
            ></v-switch>
          </template>

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
        </v-form>
      </v-col>

      <!-- Right Column - Resume History -->
      <v-col cols="12" md="6">
        <v-card class="mb-4" variant="outlined">
          <v-card-title class="text-h6 font-weight-medium">
            <v-icon icon="mdi-history" class="mr-2"></v-icon>
            Previously Generated Resumes
          </v-card-title>
          
          <v-card-text>
            <v-list v-if="resumeHistory.length">
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
                    @click="$router.push(`/resume/${resume.id}`)"
                    prepend-icon="mdi-open-in-new"
                    class="mr-2"
                  >
                    View
                  </v-btn>
                </template>
              </v-list-item>
            </v-list>
            <v-alert v-else type="info" variant="tonal">
              No previously generated resumes found
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-card>
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
  created_at: string
}

const profileData = ref({
  name: '',
  phone: '',
  location: '',
  linkedin_url: '',
  resume_path: '',
  userType: auth.user?.userType || ''
})

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

const resumeHistory = ref<ResumeHistoryItem[]>([])
const resumeFile = ref()
const hasExistingResume = ref<'yes' | 'no'>('no')
const useAsReference = ref(true)
const isValid = ref(false)
const error = ref('')
const loading = ref(false)
const deleteLoading = ref(false)

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
    const { name, phone, location, linkedin_url, resume_path, professional_info } = auth.user.profile
    profileData.value = {
      name: name || '',
      phone: phone || '',
      location: location || '',
      linkedin_url: linkedin_url || '',
      resume_path: resume_path || '',
      userType: auth.user?.userType || ''
    }

    // Auto-fill from LinkedIn data if available
    if (linkedin_url && professional_info?.linkedin_data) {
      const linkedinData = professional_info.linkedin_data
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
  if (!resumeFile.value) return
  
  try {
    loading.value = true
    const formData = new FormData()
    formData.append('resume', resumeFile.value)
    
    const response = await axios.post('/api/parse-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    const { name, phone, location } = response.data
    profileData.value = {
      ...profileData.value,
      name: name || profileData.value.name,
      phone: phone || profileData.value.phone,
      location: location || profileData.value.location
    }
  } catch (err: any) {
    error.value = 'Failed to parse resume: ' + (err.response?.data?.detail || err.toString())
  } finally {
    loading.value = false
  }
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
