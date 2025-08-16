<template>
  <v-container fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);" class="pa-4">
    <v-row>
      <!-- Main Profile Form -->
      <v-col cols="12">
        <v-card class="pa-md-8 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <!-- Main Tabs -->
          <v-tabs v-model="mainTab" color="primary" align-tabs="center" class="mb-6">
            <v-tab value="profile">
              <v-icon icon="mdi-account-circle-outline" class="mr-2"></v-icon>
              Profile
            </v-tab>
            <v-tab value="experience">
              <v-icon icon="mdi-briefcase-outline" class="mr-2"></v-icon>
              Experience
            </v-tab>
            <v-tab value="education">
              <v-icon icon="mdi-school-outline" class="mr-2"></v-icon>
              Education
            </v-tab>
            <v-tab value="skills">
              <v-icon icon="mdi-star-outline" class="mr-2"></v-icon>
              Skills
            </v-tab>
            <v-tab value="projects">
              <v-icon icon="mdi-code-tags" class="mr-2"></v-icon>
              Projects
            </v-tab>
            <v-tab value="resumes">
              <v-icon icon="mdi-file-document-multiple-outline" class="mr-2"></v-icon>
              My Resumes
              <v-chip v-if="resumeCount > 0" size="x-small" color="primary" class="ml-2">
                {{ resumeCount }}
              </v-chip>
            </v-tab>
          </v-tabs>

          <v-tabs-window v-model="mainTab">
            <!-- Profile Information Tab -->
            <v-tabs-window-item value="profile">
              <v-card-title class="text-h4 font-weight-bold mb-2 text-grey-darken-3 pa-0">
                <v-icon icon="mdi-account-circle-outline" class="mr-3" color="primary"></v-icon>
                Profile Information
              </v-card-title>
              <v-card-subtitle class="text-body-1 mb-8 text-grey-darken-1 pa-0">
                Complete your profile to unlock the full power of the resume builder.
              </v-card-subtitle>

              <!-- Basic Profile Information -->
              <v-form @submit.prevent="handleSubmit" v-model="isValid">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.name"
                      label="Full Name *"
                      :rules="[v => !!v || 'Name is required']"
                      variant="outlined"
                      density="comfortable"
                      prepend-inner-icon="mdi-account-outline"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      :model-value="auth.user?.email"
                      label="Email"
                      variant="outlined"
                      density="comfortable"
                      readonly
                      disabled
                      prepend-inner-icon="mdi-email-outline"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.phone"
                      label="Phone Number"
                      variant="outlined"
                      density="comfortable"
                      placeholder="Optional"
                      prepend-inner-icon="mdi-phone-outline"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.location"
                      label="Location"
                      variant="outlined"
                      density="comfortable"
                      placeholder="Optional"
                      prepend-inner-icon="mdi-map-marker-outline"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.professional_title"
                      label="Professional Title"
                      variant="outlined"
                      density="comfortable"
                      placeholder="e.g., Software Engineer"
                      prepend-inner-icon="mdi-briefcase-outline"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.linkedin_url"
                      label="LinkedIn Profile URL"
                      variant="outlined"
                      density="comfortable"
                      placeholder="Optional"
                      :rules="[v => !v || v.includes('linkedin.com/in/') || 'Please enter a valid LinkedIn profile URL']"
                      prepend-inner-icon="mdi-linkedin"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-row>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.portfolio_url"
                      label="Portfolio URL"
                      variant="outlined"
                      density="comfortable"
                      placeholder="Optional"
                      prepend-inner-icon="mdi-web"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="12" md="6">
                    <v-text-field
                      v-model="profileData.github_url"
                      label="GitHub URL"
                      variant="outlined"
                      density="comfortable"
                      placeholder="Optional"
                      prepend-inner-icon="mdi-github"
                    ></v-text-field>
                  </v-col>
                </v-row>

                <v-textarea
                  v-model="profileData.summary"
                  label="Professional Summary"
                  variant="outlined"
                  density="comfortable"
                  placeholder="Brief overview of your professional background and goals"
                  prepend-inner-icon="mdi-text-box-outline"
                  rows="3"
                  class="mb-4"
                ></v-textarea>

                <v-divider class="my-8" :thickness="2"></v-divider>

                <!-- Resume Upload Section -->
                <div class="text-h5 font-weight-bold mb-2 text-grey-darken-3">
                  <v-icon icon="mdi-auto-fix" class="mr-3" color="primary"></v-icon>
                  Jumpstart Your Profile with AI
                </div>
                <div class="text-body-1 text-grey-darken-1 mb-6">
                  Upload your resume, and we'll use AI to automatically fill out your profile sections.
                </div>

                <drag-drop-file-upload
                  v-model="resumeFile"
                  accept=".pdf"
                  :max-size="10"
                  :error-message="error"
                  @file-selected="handleResumeUpload"
                  class="mb-6"
                  title="Upload your Resume / CV"
                  supported-formats="PDF"
                  :loading="uploadStatus === 'uploading'"
                />

                <!-- Global Toggle for Resume Sections -->
                <v-divider class="my-8" :thickness="2"></v-divider>
                <div class="text-h6 mb-4 font-weight-medium">Profile Settings</div>
                <v-card variant="outlined" class="pa-4 mb-6" rounded="lg">
                  <v-switch
                    v-model="profileData.use_resume_sections"
                    label="Use my profile sections for resume generation"
                    color="primary"
                    inset
                    hide-details
                  ></v-switch>
                  <div class="text-caption text-grey-darken-1 mt-2">
                    When enabled, your structured profile sections will be used for resume generation. When disabled, the system will use your uploaded resume or basic profile information.
                  </div>
                </v-card>

                <v-alert v-if="error" type="error" variant="tonal" class="my-6" closable>{{ error }}</v-alert>

                <div class="d-flex justify-end mt-8">
                  <v-btn type="submit" color="primary" size="x-large" :loading="loading" :disabled="!isValid" rounded="lg" elevation="4">
                    {{ auth.hasProfile ? 'Update Profile' : 'Create Profile' }}
                  </v-btn>
                </div>
              </v-form>
            </v-tabs-window-item>

            <!-- Work Experience Tab -->
            <v-tabs-window-item value="experience">
              <WorkExperienceSection 
                :experiences="workExperiences" 
                @add="addWorkExperience"
                @edit="editWorkExperience"
                @delete="deleteWorkExperience"
              />
            </v-tabs-window-item>

            <!-- Education Tab -->
            <v-tabs-window-item value="education">
              <EducationSection 
                :educations="educations" 
                @add="addEducation"
                @edit="editEducation"
                @delete="deleteEducation"
              />
            </v-tabs-window-item>

            <!-- Skills Tab -->
            <v-tabs-window-item value="skills">
              <SkillsSection 
                :skills="skills" 
                @add="addSkill"
                @edit="editSkill"
                @delete="deleteSkill"
              />
            </v-tabs-window-item>

            <!-- Projects Tab -->
            <v-tabs-window-item value="projects">
              <ProjectsSection 
                :projects="projects" 
                @add="addProject"
                @edit="editProject"
                @delete="deleteProject"
              />
            </v-tabs-window-item>

            <!-- Saved Resumes Tab -->
            <v-tabs-window-item value="resumes">
              <div class="text-h5 font-weight-bold mb-6 text-grey-darken-3">
                <v-icon icon="mdi-file-document-multiple-outline" class="mr-3" color="primary"></v-icon>
                Your Saved Resumes
              </div>
              
              <ResumeList ref="resumeListRef" @resume-deleted="loadResumeCount" />
            </v-tabs-window-item>
          </v-tabs-window>
        </v-card>
      </v-col>
    </v-row>

    <!-- Resume Parse Preview Dialog -->
    <v-dialog v-model="showParseDialog" max-width="800" persistent>
      <v-card>
        <v-card-title class="text-h5">
          <v-icon icon="mdi-brain" class="mr-2" color="primary"></v-icon>
          AI Resume Analysis
        </v-card-title>
        <v-card-text>
          <div v-if="parseLoading" class="text-center py-8">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            <div class="mt-4">Analyzing your resume with AI...</div>
          </div>
          <div v-else-if="parsedData">
            <v-alert color="info" variant="tonal" class="mb-4">
              Review the extracted information below and click "Import" to add it to your profile sections.
            </v-alert>
            
            <v-expansion-panels multiple>
              <v-expansion-panel v-if="parsedData.work_experience?.length">
                <v-expansion-panel-title>
                  <v-icon icon="mdi-briefcase-outline" class="mr-2"></v-icon>
                  Work Experience ({{ parsedData.work_experience.length }})
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <div v-for="(exp, index) in parsedData.work_experience" :key="index" class="mb-4 pa-3 border rounded">
                    <div class="font-weight-bold">{{ exp.position }} at {{ exp.company }}</div>
                    <div class="text-caption text-grey-darken-1">{{ exp.start_date }} - {{ exp.end_date || 'Present' }}</div>
                    <div v-if="exp.description" class="mt-2">{{ exp.description }}</div>
                  </div>
                </v-expansion-panel-text>
              </v-expansion-panel>

              <v-expansion-panel v-if="parsedData.education?.length">
                <v-expansion-panel-title>
                  <v-icon icon="mdi-school-outline" class="mr-2"></v-icon>
                  Education ({{ parsedData.education.length }})
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <div v-for="(edu, index) in parsedData.education" :key="index" class="mb-4 pa-3 border rounded">
                    <div class="font-weight-bold">{{ edu.degree }} in {{ edu.field_of_study }}</div>
                    <div class="text-caption text-grey-darken-1">{{ edu.institution }}</div>
                  </div>
                </v-expansion-panel-text>
              </v-expansion-panel>

              <v-expansion-panel v-if="parsedData.skills?.length">
                <v-expansion-panel-title>
                  <v-icon icon="mdi-star-outline" class="mr-2"></v-icon>
                  Skills ({{ parsedData.skills.length }})
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <v-chip-group>
                    <v-chip v-for="skill in parsedData.skills" :key="skill.name" size="small">
                      {{ skill.name }}
                    </v-chip>
                  </v-chip-group>
                </v-expansion-panel-text>
              </v-expansion-panel>

              <v-expansion-panel v-if="parsedData.projects?.length">
                <v-expansion-panel-title>
                  <v-icon icon="mdi-code-tags" class="mr-2"></v-icon>
                  Projects ({{ parsedData.projects.length }})
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <div v-for="(project, index) in parsedData.projects" :key="index" class="mb-4 pa-3 border rounded">
                    <div class="font-weight-bold">{{ project.name }}</div>
                    <div v-if="project.description" class="mt-2">{{ project.description }}</div>
                  </div>
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="showParseDialog = false" :disabled="parseLoading">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="importParsedData" :disabled="parseLoading || !parsedData">Import Sections</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useAuthStore } from '../store/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'
import WorkExperienceSection from '@/components/profile-sections/WorkExperienceSection.vue'
import EducationSection from '@/components/profile-sections/EducationSection.vue'
import SkillsSection from '@/components/profile-sections/SkillsSection.vue'
import ProjectsSection from '@/components/profile-sections/ProjectsSection.vue'
import ResumeList from './ResumeList.vue'
import DragDropFileUpload from './DragDropFileUpload.vue'

const auth = useAuthStore()
const router = useRouter()

// Profile data
const profileData = ref({
  name: '',
  phone: '',
  location: '',
  linkedin_url: '',
  portfolio_url: '',
  github_url: '',
  professional_title: '',
  summary: '',
  resume_path: '',
  use_resume_as_reference: true,
  use_resume_sections: true
})

// Section data
const workExperiences = ref<any[]>([])
const educations = ref<any[]>([])
const skills = ref<any[]>([])
const projects = ref<any[]>([])

// UI state
const mainTab = ref('profile')
const resumeFile = ref()
const hasExistingResume = ref(false)
const isValid = ref(false)
const error = ref('')
const loading = ref(false)
const deleteLoading = ref(false)
const uploadStatus = ref<'idle' | 'uploading' | 'success' | 'error'>('idle')

// Resume list state
const resumeListRef = ref()
const resumeCount = ref(0)
// Remove this computed property as we'll always show the resumes tab

// Resume parsing
const showParseDialog = ref(false)
const parseLoading = ref(false)
const parsedData = ref<any>(null)

// Load profile data and sections
onMounted(async () => {
  if (auth.user?.profile) {
    const profile = auth.user.profile
    profileData.value = {
      name: profile.name || '',
      phone: profile.phone || '',
      location: profile.location || '',
      linkedin_url: profile.linkedin_url || '',
      portfolio_url: profile.portfolio_url || '',
      github_url: profile.github_url || '',
      professional_title: profile.professional_title || '',
      summary: profile.summary || '',
      resume_path: profile.resume_path || '',
      use_resume_as_reference: profile.use_resume_as_reference ?? true,
      use_resume_sections: profile.use_resume_sections ?? true
    }

    // Load profile sections
    await loadProfileSections()
    
    // Load resume count
    await loadResumeCount()
  }

    // No need to call loadResumeCount() here since it's already called in onMounted
})

const loadResumeCount = async () => {
  try {
    loading.value = true
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

    const response = await apiClient.get('/api/resumes')
    resumeCount.value = response.data.length
  } catch (err) {
    console.error('Failed to load resume count:', err)
    resumeCount.value = 0
  } finally {
    loading.value = false
  }
}

const loadProfileSections = async () => {
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

    const [expRes, eduRes, skillRes, projRes] = await Promise.all([
      apiClient.get('/profile/work-experience'),
      apiClient.get('/profile/education'),
      apiClient.get('/profile/skills'),
      apiClient.get('/profile/projects')
    ])

    workExperiences.value = expRes.data
    educations.value = eduRes.data
    skills.value = skillRes.data
    projects.value = projRes.data
  } catch (err) {
    console.error('Failed to load profile sections:', err)
  }
}

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
    error.value = ''
    
    const formData = new FormData()
    formData.append('resume', resumeFile.value)
    
    const uploadResponse = await axios.post('/api/upload-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${auth.token}`
      }
    })

    if (uploadResponse.status === 200 && uploadResponse.data) {
      profileData.value.resume_path = uploadResponse.data.file_path || uploadResponse.data.path
      uploadStatus.value = 'success'
      await auth.fetchUser()
      
      // Reload profile sections since they may have been populated by the upload
      await loadProfileSections()
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

const handleDeleteResume = async () => {
  try {
    deleteLoading.value = true
    await axios.delete('/api/delete-resume', {
      headers: { 'Authorization': `Bearer ${auth.token}` }
    })
    profileData.value.resume_path = ''
    await auth.fetchUser()
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.toString()
  } finally {
    deleteLoading.value = false
  }
}

const parseResumeWithAI = async () => {
  if (!profileData.value.resume_path) return

  try {
    showParseDialog.value = true
    parseLoading.value = true
    
    // First get the resume text (you might need to implement this endpoint)
    const resumeText = await getResumeText()
    
    // Parse with Groq AI
    const response = await axios.post('/api/parse-resume', 
      { resume_text: resumeText },
      { headers: { 'Authorization': `Bearer ${auth.token}` } }
    )
    
    parsedData.value = response.data
  } catch (err: any) {
    error.value = 'Failed to parse resume: ' + (err.response?.data?.detail || err.message)
    showParseDialog.value = false
  } finally {
    parseLoading.value = false
  }
}

const getResumeText = async () => {
  // This would need to be implemented to extract text from the uploaded PDF
  // For now, return a placeholder
  return "Resume text would be extracted here"
}

const importParsedData = async () => {
  if (!parsedData.value) return

  try {
    loading.value = true
    await axios.post('/api/import-resume-sections', parsedData.value, {
      headers: { 'Authorization': `Bearer ${auth.token}` }
    })
    
    // Reload sections
    await loadProfileSections()
    showParseDialog.value = false
    parsedData.value = null
  } catch (err: any) {
    error.value = 'Failed to import sections: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

// Create a reusable API client function
const createApiClient = () => {
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

  return apiClient
}

// Section management functions
const addWorkExperience = async (experience: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.post('/profile/work-experience', experience)
    workExperiences.value.push(response.data)
  } catch (err: any) {
    error.value = 'Failed to add work experience: ' + (err.response?.data?.detail || err.message)
  }
}

const editWorkExperience = async (id: string, experience: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.put(`/profile/work-experience/${id}`, experience)
    const index = workExperiences.value.findIndex(exp => exp.id === id)
    if (index !== -1) {
      workExperiences.value[index] = response.data
    }
  } catch (err: any) {
    error.value = 'Failed to update work experience: ' + (err.response?.data?.detail || err.message)
  }
}

const deleteWorkExperience = async (id: string) => {
  try {
    const apiClient = createApiClient()
    await apiClient.delete(`/profile/work-experience/${id}`)
    workExperiences.value = workExperiences.value.filter(exp => exp.id !== id)
  } catch (err: any) {
    error.value = 'Failed to delete work experience: ' + (err.response?.data?.detail || err.message)
  }
}

const addEducation = async (education: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.post('/profile/education', education)
    educations.value.push(response.data)
  } catch (err: any) {
    error.value = 'Failed to add education: ' + (err.response?.data?.detail || err.message)
  }
}

const editEducation = async (id: string, education: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.put(`/profile/education/${id}`, education)
    const index = educations.value.findIndex(edu => edu.id === id)
    if (index !== -1) {
      educations.value[index] = response.data
    }
  } catch (err: any) {
    error.value = 'Failed to update education: ' + (err.response?.data?.detail || err.message)
  }
}

const deleteEducation = async (id: string) => {
  try {
    const apiClient = createApiClient()
    await apiClient.delete(`/profile/education/${id}`)
    educations.value = educations.value.filter(edu => edu.id !== id)
  } catch (err: any) {
    error.value = 'Failed to delete education: ' + (err.response?.data?.detail || err.message)
  }
}

const addSkill = async (skill: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.post('/profile/skills', skill)
    skills.value.push(response.data)
  } catch (err: any) {
    error.value = 'Failed to add skill: ' + (err.response?.data?.detail || err.message)
  }
}

const editSkill = async (id: string, skill: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.put(`/profile/skills/${id}`, skill)
    const index = skills.value.findIndex(s => s.id === id)
    if (index !== -1) {
      skills.value[index] = response.data
    }
  } catch (err: any) {
    error.value = 'Failed to update skill: ' + (err.response?.data?.detail || err.message)
  }
}

const deleteSkill = async (id: string) => {
  try {
    const apiClient = createApiClient()
    await apiClient.delete(`/profile/skills/${id}`)
    skills.value = skills.value.filter(s => s.id !== id)
  } catch (err: any) {
    error.value = 'Failed to delete skill: ' + (err.response?.data?.detail || err.message)
  }
}

const addProject = async (project: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.post('/profile/projects', project)
    projects.value.push(response.data)
  } catch (err: any) {
    error.value = 'Failed to add project: ' + (err.response?.data?.detail || err.message)
  }
}

const editProject = async (id: string, project: any) => {
  try {
    const apiClient = createApiClient()
    const response = await apiClient.put(`/profile/projects/${id}`, project)
    const index = projects.value.findIndex(p => p.id === id)
    if (index !== -1) {
      projects.value[index] = response.data
    }
  } catch (err: any) {
    error.value = 'Failed to update project: ' + (err.response?.data?.detail || err.message)
  }
}

const deleteProject = async (id: string) => {
  try {
    const apiClient = createApiClient()
    await apiClient.delete(`/profile/projects/${id}`)
    projects.value = projects.value.filter(p => p.id !== id)
  } catch (err: any) {
    error.value = 'Failed to delete project: ' + (err.response?.data?.detail || err.message)
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
      portfolio_url: profileData.value.portfolio_url,
      github_url: profileData.value.github_url,
      professional_title: profileData.value.professional_title,
      summary: profileData.value.summary,
      resume_path: profileData.value.resume_path,
      use_resume_as_reference: profileData.value.use_resume_as_reference,
      use_resume_sections: profileData.value.use_resume_sections
    }

    if (auth.hasProfile) {
      await auth.updateProfile(data)
    } else {
      await auth.createProfile(data)
    }

    await auth.fetchUser()
    
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
