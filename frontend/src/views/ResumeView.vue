<template>
  <v-container class="fill-height pa-0" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row no-gutters class="fill-height">
      <!-- Left Column - Template Selection -->
      <v-col cols="12" md="4" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-md-6 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="text-h5 font-weight-bold mb-4 text-grey-darken-3">
            Select a Template
          </v-card-title>
          <v-carousel
            v-model="selectedTemplateIndex"
            height="calc(100vh - 240px)"
            show-arrows="hover"
            hide-delimiters
            class="template-carousel"
            :disabled="loadingTemplates"
          >
            <template v-slot:prev="{ props }">
              <v-btn v-bind="props" icon="mdi-chevron-left" variant="text" color="primary"></v-btn>
            </template>
            <template v-slot:next="{ props }">
              <v-btn v-bind="props" icon="mdi-chevron-right" variant="text" color="primary"></v-btn>
            </template>
            
            <v-progress-circular v-if="loadingTemplates" indeterminate color="primary" size="64" class="ma-auto"></v-progress-circular>
            
            <v-carousel-item v-for="(template, index) in availableTemplates" :key="template.id" :value="index">
              <v-card class="d-flex flex-column h-100" flat color="transparent">
                <div class="template-image-container" style="height: 70%; margin-bottom: 16px;">
                  <v-img
                    :src="templatePreviews[template.id]"
                    aspect-ratio="0.707"
                    contain
                    class="template-preview elevation-6"
                    style="width: 100%; height: 100%;"
                  ></v-img>
                </div>
                <div class="template-info" style="height: 30%; display: flex; flex-direction: column;">
                  <v-card-title class="text-center pa-2 text-h6 font-weight-medium flex-shrink-0">{{ template.name }}</v-card-title>
                  <v-card-text class="text-center px-2 pb-2 text-body-2 flex-grow-1" style="white-space: normal; line-height: 1.5; overflow-y: auto;">
                    {{ template.description }}
                  </v-card-text>
                </div>
              </v-card>
            </v-carousel-item>
          </v-carousel>
        </v-card>
      </v-col>

      <!-- Right Column - Resume Preview -->
      <v-col cols="12" md="8" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-md-6 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="text-h5 font-weight-bold mb-4 text-grey-darken-3 d-flex justify-space-between align-center">
            <div class="d-flex align-center">
              <v-btn 
                icon="mdi-arrow-left" 
                variant="text" 
                @click="$router.push({ path: '/profile', query: { tab: 'resumes' } })" 
                class="mr-2"
              ></v-btn>
              <div>
                Resume Preview
                <div class="text-caption">{{ formattedResumeName }}</div>
              </div>
            </div>
            <div class="d-flex align-center gap-2">
              <v-btn
                color="primary"
                variant="flat"
                :prepend-icon="isEditing ? 'mdi-content-save' : 'mdi-pencil'"
                @click="handleEditSave"
                :loading="saving"
                :disabled="saving"
              >
                {{ isEditing ? 'Save' : 'Edit' }}
              </v-btn>
              <v-alert
                v-if="saveError"
                type="error"
                variant="tonal"
                density="compact"
                class="mb-0"
              >
                {{ saveError }}
              </v-alert>
            </div>
          </v-card-title>

          <v-card-text class="overflow-y-auto flex-grow-1" style="max-height: calc(100vh - 240px);">
            <v-progress-circular v-if="loadingResume" indeterminate color="primary" size="64" class="ma-auto d-block"></v-progress-circular>
            <template v-else>
              <v-textarea
                v-if="isEditing"
                v-model="editableContent"
                variant="outlined"
                auto-grow
                class="resume-editor"
                hide-details
                filled
              />
              <div v-else class="resume-preview" v-html="formattedResumeContent" />
            </template>
          </v-card-text>

          <v-card-actions class="pa-4">
            <v-alert v-if="showOverflowWarning" type="warning" variant="tonal" class="mr-4" density="compact">
              {{ overflowMessage }}
            </v-alert>
            <v-spacer></v-spacer>
            <div class="d-flex gap-3">
              <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-file-pdf-box"
                @click="downloadPdf"
                :loading="pdfLoading"
                size="large"
              >
                Download PDF
              </v-btn>
              <v-btn
                color="primary"
                variant="flat"
                prepend-icon="mdi-file-word"
                @click="downloadDocx"
                :loading="docxLoading"
                size="large"
              >
                Download Word
              </v-btn>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <PaymentDialog 
      v-model="paymentDialog"
      :credits="auth.user?.credits || 0"
      :resume-file="lastGeneratedFile"
      @payment-completed="onPaymentCompleted"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useResumeStore } from '@/store/resume'
import { useAuthStore } from '@/store/auth'
import PaymentDialog from '@/components/PaymentDialog.vue'
import axios from 'axios'
import { marked } from 'marked'

const route = useRoute()
const resumeStore = useResumeStore()
const auth = useAuthStore()

const companyName = ref('')
const jobTitle = ref('')

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

// Template selection
const availableTemplates = ref<Array<{id: string, name: string, description: string}>>([])
const selectedTemplateIndex = ref(0)
const loadingTemplates = ref(false)
const templatePreviews = ref<Record<string, string>>({})
const selectedTemplate = computed({
  get: () => availableTemplates.value[selectedTemplateIndex.value]?.id || 'professional',
  set: (newId) => {
    const index = availableTemplates.value.findIndex(t => t.id === newId)
    if (index >= 0) {
      selectedTemplateIndex.value = index
    }
  }
})

// Resume preview
const isEditing = ref(false)
const pdfLoading = ref(false)
const docxLoading = ref(false)
const editableContent = ref('')
const resumeData = ref<any>(null)
const generatedResume = computed(() => resumeData.value?.content || resumeStore.result?.content || '')

// Payment dialog
const paymentDialog = ref(false)
const lastGeneratedFile = ref('')

// Overflow warning
const showOverflowWarning = ref(false)
const overflowMessage = ref('')

const initializeEditableContent = () => {
  editableContent.value = generatedResume.value
}

const saving = ref(false)
const saveError = ref('')

  const handleEditSave = async () => {
    if (isEditing.value) {
      try {
        saving.value = true
        saveError.value = ''
        // Ensure we get a string ID (handle case where route.params.id might be an array)
        const routeId = Array.isArray(route.params.id) ? route.params.id[0] : route.params.id
        const resumeId = routeId || resumeStore.jobId
        await resumeStore.updateResumeContent(editableContent.value, resumeId as string)
        
        // Refresh resume data after successful save
        if (routeId) {
          await fetchResumeById(routeId)
        }
    } catch (error: any) {
      console.error('Error saving resume:', error)
      saveError.value = error.message || 'Failed to save changes'
    } finally {
      saving.value = false
    }
  } else {
    initializeEditableContent()
  }
  isEditing.value = !isEditing.value
}

const formattedResumeName = computed(() => {
  if (!resumeData.value) return ''
  const profileName = auth.user?.profile?.name || 'user'
  const date = new Date(resumeData.value.created_at).toISOString().split('T')[0]
  if (resumeData.value.job_title && resumeData.value.company_name) {
    return `${profileName}_Resume_for_${resumeData.value.job_title}_${resumeData.value.company_name}_${date}`
  }
  return `${profileName}_Resume_${date}`
})

const formattedResumeContent = computed(() => {
  console.log('Raw resume content:', generatedResume.value)
  if (!hasResumeContent.value) {
    return '<div class="empty-resume">No resume content available. Please generate a resume first.</div>'
  }
  if (!generatedResume.value) {
    return '<div class="empty-resume">Resume content is empty</div>'
  }
  try {
    const html = marked(generatedResume.value, { breaks: true })
    console.log('Processed HTML:', html)
    return html
  } catch (e) {
    console.error('Markdown processing error:', e)
    return generatedResume.value // Fallback to raw content
  }
})

const checkCredits = async () => {
  try {
    await auth.fetchUser()
    return (auth.user?.credits || 0) > 0
  } catch (error) {
    console.error('Error checking credits:', error)
    return false
  }
}

const downloadPdf = async () => {
  if (!generatedResume.value) return
  
  try {
    pdfLoading.value = true
    showOverflowWarning.value = false

    // Validate template selection
    if (!selectedTemplate.value || !availableTemplates.value.length) {
      throw new Error('Please select a template first')
    }

    const response = await apiClient.post('/generate-pdf', {
      ai_content: generatedResume.value,
      job_title: resumeData.value?.name || resumeStore.result?.job_title || 'Resume',
      agent_outputs: resumeStore.result?.agent_outputs || '',
      template_id: selectedTemplate.value
    })
    
    // Check for overflow warning
    if (response.data.overflow) {
      showOverflowWarning.value = true
      overflowMessage.value = response.data.message || 
        'The content exceeds the space available in this template. ' +
        'Please either:\n' +
        '1. Edit and shorten your content, or\n' + 
        '2. Select a different template with more space'
    }
    
    lastGeneratedFile.value = response.data.pdf_url
    
    // Download the PDF
    const pdfResponse = await apiClient.get(response.data.pdf_url, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([pdfResponse.data]))
    const link = document.createElement('a')
    link.href = url
    const profileName = auth.user?.profile?.name || 'user'
    const jobTitle = resumeData.value?.job_title || resumeStore.result?.job_title || 'resume'
    const companyName = resumeData.value?.company_name || 'company'
    const date = new Date().toISOString().split('T')[0]
    const filename = `${profileName}_Resume_for_${jobTitle}_${companyName}_${date}.pdf`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('Error generating/downloading PDF:', error)
    if (axios.isAxiosError(error) && error.response?.status === 402) {
      paymentDialog.value = true
    } else {
      // Show user-friendly error message
      showOverflowWarning.value = true
      overflowMessage.value = error.message || 'Failed to generate PDF. Please try again.'
    }
  } finally {
    pdfLoading.value = false
  }
}

const downloadDocx = async () => {
  if (!generatedResume.value) return
  
  try {
    docxLoading.value = true
    const response = await apiClient.post('/generate-resume-docx', {
      ai_content: generatedResume.value,
      job_title: resumeData.value?.name || resumeStore.result?.job_title || 'Resume'
    })
    
    // Download the DOCX
    const docxResponse = await apiClient.get(response.data.docx_url, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([docxResponse.data]))
    const link = document.createElement('a')
    link.href = url
    const profileName = auth.user?.profile?.name || 'user'
    const jobTitle = resumeData.value?.job_title || resumeStore.result?.job_title || 'resume'
    const companyName = resumeData.value?.company_name || 'company'
    const date = new Date().toISOString().split('T')[0]
    const filename = `${profileName}_Resume_for_${jobTitle}_${companyName}_${date}.docx`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('Error generating/downloading Word document:', error)
    if (axios.isAxiosError(error) && error.response?.status === 402) {
      paymentDialog.value = true
    }
  } finally {
    docxLoading.value = false
  }
}

const onPaymentCompleted = async () => {
  await auth.fetchUser()
  paymentDialog.value = false
}

const loadingResume = ref(true)
const hasResumeContent = ref(false)

const fetchResumeById = async (resumeId: string) => {
  try {
    loadingResume.value = true
    const response = await apiClient.get(`/resume/${resumeId}`)
    resumeData.value = response.data
    hasResumeContent.value = true
    console.log('Fetched resume from database:', response.data)
    return response.data
  } catch (error: any) {
    console.error('Error fetching resume by ID:', error)
    if (error.response?.status === 404) {
      throw new Error('Resume not found')
    }
    throw error
  } finally {
    loadingResume.value = false
  }
}

onMounted(async () => {
  console.log('ResumeView mounted - route params:', route.params)
  
  // Get resume ID from route parameters
  const resumeId = route.params.id as string
  
  if (resumeId) {
    try {
      await fetchResumeById(resumeId)
    } catch (error: any) {
      console.error('Failed to fetch resume:', error.message)
      hasResumeContent.value = false
    }
  } else {
    // Fallback to store content if no ID in route
    console.log('No resume ID in route, checking store content:', resumeStore.result?.content)
    
    if (resumeStore.result?.content) {
      hasResumeContent.value = true
      loadingResume.value = false
    } else if (resumeStore.jobId) {
      try {
        loadingResume.value = true
        await resumeStore.getResult()
        if (resumeStore.result?.content) {
          hasResumeContent.value = true
        }
        console.log('Fetched resume content from store:', resumeStore.result?.content)
      } catch (error) {
        console.error('Error fetching resume result:', error)
      } finally {
        loadingResume.value = false
      }
    } else {
      console.warn('No resume content available and no jobId to fetch from')
      loadingResume.value = false
    }
  }

  await resumeStore.fetchTemplates();
  availableTemplates.value = resumeStore.templates;
  
  // Load template preview images
  templatePreviews.value = {
    professional: `/template-previews/template_Professional.png`,
    modern: `/template-previews/template_Modern.png`,
    executive: `/template-previews/template_Executive.png`,
    classic: `/template-previews/template_Classic.png`,
    compact: `/template-previews/template_Compact.png`,
    dense: `/template-previews/template_Dense.png`,
    elegant: `/template-previews/template_Elegant.png`
  };

  // Set default template if available
  const defaultTemplate = availableTemplates.value.find((t: any) => t.is_default);
  if (defaultTemplate) {
    selectedTemplate.value = defaultTemplate.id;
  }

  initializeEditableContent()
})
</script>

<style scoped>
.template-carousel {
  border-radius: 16px;
}

.template-preview {
  border-radius: 8px;
  width: 100%;
  object-fit: cover;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.template-preview:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.resume-preview {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  line-height: 1.7;
  font-size: 0.95rem;
}

.resume-editor {
  font-size: 0.95rem;
  line-height: 1.7;
}

.d-flex.gap-3 > * {
  margin-left: 12px;
}
.d-flex.gap-3 > *:first-child {
  margin-left: 0;
}

@media (max-width: 1279px) {
  .v-col {
    padding: 12px !important;
  }
}
</style>
