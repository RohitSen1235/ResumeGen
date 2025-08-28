<template>
  <v-container class="fill-height pa-0" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row no-gutters class="fill-height">
      <!-- Left Column - Template Selection -->
      <v-col cols="12" md="3" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="text-h6 font-weight-bold mb-4 text-grey-darken-3">
            Template
          </v-card-title>
          
          <!-- Template Preview -->
          <div class="template-preview-container mb-4">
            <v-img
              v-if="selectedTemplate"
              :src="selectedTemplate.image_path"
              aspect-ratio="0.707"
              contain
              class="template-preview elevation-4"
              style="border-radius: 8px;"
            ></v-img>
          </div>
          
          <!-- Template Selector -->
          <v-select
            v-model="selectedTemplateId"
            :items="availableTemplates"
            item-title="name"
            item-value="id"
            label="Select Template"
            variant="outlined"
            density="comfortable"
            @update:model-value="onTemplateChange"
          ></v-select>
          
          <!-- Actions -->
          <div class="mt-4">
            <v-btn
              color="primary"
              variant="flat"
              prepend-icon="mdi-content-save"
              @click="saveResume"
              :loading="saving"
              :disabled="saving"
              block
              class="mb-2"
            >
              Save Changes
            </v-btn>
            
            <v-btn
              color="success"
              variant="flat"
              prepend-icon="mdi-file-pdf-box"
              @click="downloadPdf"
              :loading="pdfLoading"
              block
            >
              Download PDF
            </v-btn>
          </div>
        </v-card>
      </v-col>

      <!-- Right Column - WYSIWYG Editor -->
      <v-col cols="12" md="9" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="text-h6 font-weight-bold mb-4 text-grey-darken-3 d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-btn 
                icon="mdi-arrow-left" 
                variant="text" 
                @click="$router.push({ path: '/profile', query: { tab: 'resumes' } })" 
                class="mr-2"
              ></v-btn>
              <div>
                Resume Editor
                <div class="text-caption">{{ resumeMetadata?.job_title }} at {{ resumeMetadata?.company_name }}</div>
              </div>
            </div>
            
            <v-chip
              v-if="hasUnsavedChanges"
              color="warning"
              size="small"
              prepend-icon="mdi-circle"
            >
              Unsaved Changes
            </v-chip>
          </v-card-title>

          <v-card-text class="overflow-y-auto flex-grow-1" style="max-height: calc(90vh - 200px);">
            <v-progress-circular 
              v-if="loading" 
              indeterminate 
              color="primary" 
              size="64" 
              class="ma-auto d-block"
            ></v-progress-circular>
            
            <template v-else-if="templateDefinition && resumeData">
              <TemplateRenderer
                :template-definition="templateDefinition"
                :resume-data="resumeData"
                :personal-info="personalInfo"
                :editable="true"
                @update:resume-data="onResumeDataUpdate"
                @update:personal-info="onPersonalInfoUpdate"
              />
            </template>
            
            <v-alert
              v-else-if="error"
              type="error"
              variant="tonal"
              class="ma-4"
            >
              {{ error }}
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Save Success Snackbar -->
    <v-snackbar
      v-model="saveSuccessSnackbar"
      color="success"
      timeout="3000"
    >
      Resume saved successfully!
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="saveSuccessSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>

    <!-- Error Snackbar -->
    <v-snackbar
      v-model="errorSnackbar"
      color="error"
      timeout="5000"
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="errorSnackbar = false"
        >
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResumeStore } from '@/store/resume'
import { useAuthStore } from '@/store/auth'
import TemplateRenderer from '@/components/TemplateRenderer.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const resumeStore = useResumeStore()
const auth = useAuthStore()

// Configure axios with backend URL
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
})

// Add auth interceptor
apiClient.interceptors.request.use((config) => {
  const token = auth.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Reactive data
const loading = ref(true)
const saving = ref(false)
const pdfLoading = ref(false)
const error = ref('')
const errorMessage = ref('')
const errorSnackbar = ref(false)
const saveSuccessSnackbar = ref(false)

// Template data
const availableTemplates = ref<Array<{id: string, name: string, description: string, image_path?: string}>>([])
const selectedTemplateId = ref('Classic')
const templateDefinition = ref<any>(null)

// Resume data
const resumeData = ref<any>(null)
const personalInfo = ref<any>(null)
const resumeMetadata = ref<any>(null)
const originalResumeData = ref<any>(null)
const originalPersonalInfo = ref<any>(null)

// Computed properties
const selectedTemplate = computed(() => 
  availableTemplates.value.find(t => t.id === selectedTemplateId.value)
)

const hasUnsavedChanges = computed(() => {
  if (!originalResumeData.value || !originalPersonalInfo.value) return false
  
  return JSON.stringify(resumeData.value) !== JSON.stringify(originalResumeData.value) ||
         JSON.stringify(personalInfo.value) !== JSON.stringify(originalPersonalInfo.value)
})

// Methods
const loadTemplates = async () => {
  try {
    await resumeStore.fetchTemplates()
    availableTemplates.value = resumeStore.templates
  } catch (err: any) {
    error.value = 'Failed to load templates'
    console.error('Error loading templates:', err)
  }
}

const loadTemplateDefinition = async (templateId: string) => {
  try {
    const response = await apiClient.get(`/templates/${templateId}/definition`)
    templateDefinition.value = response.data
  } catch (err: any) {
    error.value = 'Failed to load template definition'
    console.error('Error loading template definition:', err)
  }
}

const loadResumeData = async (resumeId: string) => {
  try {
    const response = await apiClient.get(`/resume/${resumeId}/editor-data`)
    resumeData.value = response.data.structured_data
    personalInfo.value = response.data.personal_info
    resumeMetadata.value = response.data.metadata
    
    // Store original data for change detection
    originalResumeData.value = JSON.parse(JSON.stringify(response.data.structured_data))
    originalPersonalInfo.value = JSON.parse(JSON.stringify(response.data.personal_info))
  } catch (err: any) {
    error.value = 'Failed to load resume data'
    console.error('Error loading resume data:', err)
  }
}

const onTemplateChange = async (newTemplateId: string) => {
  if (newTemplateId) {
    await loadTemplateDefinition(newTemplateId)
  }
}

const onResumeDataUpdate = (newData: any) => {
  resumeData.value = { ...newData }
}

const onPersonalInfoUpdate = (newInfo: any) => {
  personalInfo.value = { ...newInfo }
}

const saveResume = async () => {
  if (!route.params.id) return
  
  try {
    saving.value = true
    
    const updateData = {
      structured_data: resumeData.value,
      personal_info: personalInfo.value
    }
    
    await apiClient.put(`/resume/${route.params.id}/editor-data`, updateData)
    
    // Update original data to reflect saved state
    originalResumeData.value = JSON.parse(JSON.stringify(resumeData.value))
    originalPersonalInfo.value = JSON.parse(JSON.stringify(personalInfo.value))
    
    saveSuccessSnackbar.value = true
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to save resume'
    errorSnackbar.value = true
    console.error('Error saving resume:', err)
  } finally {
    saving.value = false
  }
}

const downloadPdf = async () => {
  if (!resumeData.value || !personalInfo.value) return
  
  try {
    pdfLoading.value = true
    
    // Convert structured data back to the format expected by the PDF generator
    const pdfData = {
      ai_content: convertStructuredToMarkdown(resumeData.value),
      job_title: resumeMetadata.value?.job_title || 'Resume',
      template_id: selectedTemplateId.value
    }
    
    const response = await apiClient.post('/generate-pdf', pdfData)
    
    // Download the PDF
    const pdfResponse = await apiClient.get(response.data.pdf_url, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([pdfResponse.data]))
    const link = document.createElement('a')
    link.href = url
    const filename = `${personalInfo.value.name}_Resume_${new Date().toISOString().split('T')[0]}.pdf`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (err: any) {
    errorMessage.value = err.response?.data?.detail || 'Failed to generate PDF'
    errorSnackbar.value = true
    console.error('Error generating PDF:', err)
  } finally {
    pdfLoading.value = false
  }
}

const convertStructuredToMarkdown = (structuredData: any): string => {
  // This is a simplified conversion - the backend has the full implementation
  let markdown = ''
  
  for (const [sectionName, sectionData] of Object.entries(structuredData)) {
    markdown += `# ${sectionName}\n===\n`
    
    if (sectionData && typeof sectionData === 'object') {
      const data = sectionData as any
      if (data.type === 'text') {
        markdown += `${data.content}\n`
      } else if (data.type === 'skills' && data.items) {
        data.items.forEach((skill: string) => {
          markdown += `• ${skill}\n`
        })
      }
      // Add more conversion logic as needed
    }
    
    markdown += '===\n\n'
  }
  
  return markdown
}

// Lifecycle
onMounted(async () => {
  const resumeId = route.params.id as string
  
  if (!resumeId) {
    error.value = 'Resume ID not provided'
    loading.value = false
    return
  }
  
  try {
    // Load templates and resume data in parallel
    await Promise.all([
      loadTemplates(),
      loadResumeData(resumeId)
    ])
    
    // Load template definition for the default template
    await loadTemplateDefinition(selectedTemplateId.value)
  } catch (err) {
    console.error('Error during initialization:', err)
  } finally {
    loading.value = false
  }
})

// Watch for route changes
watch(() => route.params.id, async (newId) => {
  if (newId) {
    loading.value = true
    await loadResumeData(newId as string)
    loading.value = false
  }
})
</script>

<style scoped>
.template-preview-container {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.template-preview {
  max-height: 100%;
  width: auto;
}

.fill-height {
  min-height: 100vh;
}

@media (max-width: 1279px) {
  .v-col {
    padding: 12px !important;
  }
}
</style>