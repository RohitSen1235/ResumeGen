<template>
  <v-container class="fill-height pa-0" fluid>
    <v-row no-gutters class="fill-height">
      <!-- Left Column - Template Selection -->
      <v-col cols="12" md="4" lg="4" xl="3" class="pa-2 pa-sm-4" style="max-width: 480px; min-width: 320px; flex: 0 0 auto;">
        <v-card class="h-100 pa-4" elevation="8" rounded="lg" style="width: 100%;">
          <v-card-title class="text-h4 mb-4">
            <v-icon icon="mdi-file-account" class="mr-2"></v-icon>
            Select Template
          </v-card-title>

          <!-- Enhanced Template Selection Carousel -->
          <v-carousel
            v-model="selectedTemplateIndex"
            :height="$vuetify.display.mobile ? 450 : $vuetify.display.smAndDown ? 550 : 650"
            show-arrows="hover"
            hide-delimiters
            class="template-carousel"
            :disabled="loadingTemplates"
          >
            <template v-slot:prev="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-chevron-left"
                variant="text"
                :disabled="loadingTemplates"
                size="large"
              ></v-btn>
            </template>
            <template v-slot:next="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-chevron-right"
                variant="text"
                :disabled="loadingTemplates"
                size="large"
              ></v-btn>
            </template>
            
            <v-progress-circular
              v-if="loadingTemplates"
              indeterminate
              color="primary"
              size="64"
              class="ma-auto"
            ></v-progress-circular>
            <v-carousel-item
              v-for="(template, index) in availableTemplates"
              :key="template.id"
              :value="index"
            >
              <v-card class="d-flex flex-column h-100" flat>
                <div 
                  class="d-flex justify-center align-center template-image-container" 
                  :style="{
                    height: $vuetify.display.mobile ? '320px' : 
                            $vuetify.display.smAndDown ? '420px' : '520px',
                    overflow: 'hidden',
                    padding: '8px',
                    backgroundColor: '#f5f5f5',
                    borderRadius: '8px'
                  }"
                >
                  <v-img
                    :src="templatePreviews[template.id]"
                    :aspect-ratio="0.707"
                    contain
                    :max-height="$vuetify.display.mobile ? 304 : $vuetify.display.smAndDown ? 404 : 504"
                    :max-width="$vuetify.display.mobile ? 215 : $vuetify.display.smAndDown ? 285 : 356"
                    class="template-preview"
                    style="object-fit: contain; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin: 0 auto;"
                  ></v-img>
                </div>
                <v-card-title 
                  class="text-center pt-3"
                  :class="$vuetify.display.mobile ? 'text-body-1' : 'text-h6'"
                >
                  {{ template.name }}
                </v-card-title>
                <v-card-subtitle 
                  class="text-center pb-2 template-description"
                  :class="$vuetify.display.mobile ? 'text-caption' : 'text-caption'"
                  style="white-space: normal; word-wrap: break-word; line-height: 1.3; min-height: 40px; display: flex; align-items: center; justify-content: center;"
                >
                  {{ template.description }}
                </v-card-subtitle>
              </v-card>
            </v-carousel-item>
          </v-carousel>
        </v-card>
      </v-col>

      <!-- Right Column - Resume Preview -->
      <v-col cols="12" md="8" lg="8" xl="9" class="pa-2 pa-sm-4" style="flex: 1 1 auto;">
        <v-card class="h-100 pa-4 pa-lg-6" elevation="8" rounded="lg">
          <v-card-title class="text-h4 mb-4 d-flex align-center">
            <v-icon icon="mdi-file-account" class="mr-2"></v-icon>
            Resume Preview
            <v-spacer></v-spacer>
            <v-btn
              color="orange-lighten-2"
              variant="tonal"
              prepend-icon="mdi-arrow-left"
              @click="$router.go(-1)"
              size="default"
            >
              Back
            </v-btn>
          </v-card-title>

          <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 180px); padding: 0 24px 24px 24px;">
            <v-btn
              color="orange-lighten-2"
              variant="tonal"
              prepend-icon="mdi-pencil"
              @click="handleEditSave"
              class="mb-4"
            >
              {{ isEditing ? 'Save' : 'Edit' }}
            </v-btn>

            <v-progress-circular
              v-if="loadingResume"
              indeterminate
              color="primary"
              size="64"
              class="ma-auto"
            ></v-progress-circular>
            
            <template v-else>
              <v-textarea
                v-if="isEditing"
                v-model="editableContent"
                variant="plain"
                auto-grow
                rows="10"
                class="resume-editor"
                hide-details
              />
              <div 
                v-else 
                class="resume-preview" 
                v-html="formattedResumeContent"
              />
            </template>

            <v-divider class="my-4"></v-divider>

            <v-alert
              v-if="showOverflowWarning"
              type="warning"
              variant="tonal"
              class="mb-4"
            >
              {{ overflowMessage }}
            </v-alert>

            <div class="d-flex gap-2">
              <v-btn
                color="orange-lighten-2"
                variant="tonal"
                prepend-icon="mdi-file-pdf-box"
                @click="downloadPdf"
                :loading="pdfLoading"
              >
                Download PDF
              </v-btn>

              <v-btn
                color="orange-lighten-2"
                variant="tonal"
                prepend-icon="mdi-file-word"
                @click="downloadDocx"
                :loading="docxLoading"
              >
                Download Word
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Payment Dialog -->
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
const generatedResume = computed(() => resumeData.value?.content || resumeStore.state.result?.content || '')

// Payment dialog
const paymentDialog = ref(false)
const lastGeneratedFile = ref('')

// Overflow warning
const showOverflowWarning = ref(false)
const overflowMessage = ref('')

const initializeEditableContent = () => {
  editableContent.value = generatedResume.value
}

const handleEditSave = () => {
  if (isEditing.value) {
    resumeStore.updateResumeContent(editableContent.value)
  } else {
    initializeEditableContent()
  }
  isEditing.value = !isEditing.value
}

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

const fetchTemplates = async () => {
  try {
    loadingTemplates.value = true
    const response = await apiClient.get('/templates')
    
    if (response.data?.templates?.length) {
      availableTemplates.value = response.data.templates
      
      // Load template preview images
      templatePreviews.value = {
        professional: `/template-previews/template_Professional.png`,
        modern: `/template-previews/template_Modern.png`,
        executive: `/template-previews/template_Executive.png`,
        classic: `/template-previews/template_Classic.png`,
        compact: `/template-previews/template_Compact.png`,
        dense: `/template-previews/template_Dense.png`,
        elegant: `/template-previews/template_Elegant.png`
      }
      
      // Set default template if available
      const defaultTemplate = response.data.templates.find((t: any) => t.is_default)
      if (defaultTemplate) {
        selectedTemplate.value = defaultTemplate.id
      }
    }
  } catch (error) {
    console.error('Error fetching templates:', error)
  } finally {
    loadingTemplates.value = false
  }
}

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
      job_title: resumeData.value?.name || resumeStore.state.result?.job_title || 'Resume',
      agent_outputs: resumeStore.state.result?.agent_outputs || '',
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
    const filename = resumeStore.state.result?.job_title ?
      `resume-${resumeStore.state.result.job_title}-${new Date().toISOString().split('T')[0]}.pdf` :
      `resume-${new Date().toISOString().split('T')[0]}.pdf`
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
      job_title: resumeData.value?.name || resumeStore.state.result?.job_title || 'Resume'
    })
    
    // Download the DOCX
    const docxResponse = await apiClient.get(response.data.docx_url, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([docxResponse.data]))
    const link = document.createElement('a')
    link.href = url
    const filename = resumeStore.state.result?.job_title ?
      `resume-${resumeStore.state.result.job_title}-${new Date().toISOString().split('T')[0]}.docx` :
      `resume-${new Date().toISOString().split('T')[0]}.docx`
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
    console.log('No resume ID in route, checking store content:', resumeStore.state.result?.content)
    
    if (resumeStore.state.result?.content) {
      hasResumeContent.value = true
      loadingResume.value = false
    } else if (resumeStore.state.jobId) {
      try {
        loadingResume.value = true
        await resumeStore.getResult()
        if (resumeStore.state.result?.content) {
          hasResumeContent.value = true
        }
        console.log('Fetched resume content from store:', resumeStore.state.result?.content)
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

  fetchTemplates()
  initializeEditableContent()
})
</script>

<style scoped>
.template-carousel {
  margin: 0 -4px !important;
}

.template-image-container {
  padding: 0 !important;
  margin: 0 !important;
}

.template-preview {
  max-width: 100% !important;
  width: 100% !important;
  height: auto !important;
  object-fit: contain !important;
}

.resume-preview {
  width: 100%;
  max-width: 100%;
  padding: 20px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
  overflow-x: hidden;
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  box-sizing: border-box;
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  font-size: 1rem;
  border: 1px solid rgba(var(--v-border-color), 0.12);
  
  /* Ensure markdown elements are styled */
  h1, h2, h3, h4, h5, h6 {
    margin: 1em 0 0.5em;
    line-height: 1.2;
  }
  p {
    margin: 0 0 1em;
  }
  ul, ol {
    padding-left: 2em;
    margin: 0 0 1em;
  }
  li {
    margin: 0.25em 0;
  }
}

.empty-resume {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 2em;
}

.resume-editor {
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  padding: 20px;
  line-height: 1.6;
  font-size: 1rem;
  width: 100%;
  min-height: calc(100vh - 300px);
  border: 1px solid rgba(var(--v-border-color), 0.12);
}

@media (max-width: 675px) {
  .resume-preview, .resume-editor {
    max-height: 400px;
    padding: 12px;
    font-size: 0.9rem;
  }
}

@media (min-width: 1920px) {
  .resume-preview, .resume-editor {
    font-size: 1.1rem;
    padding: 24px;
  }
}

@media (min-width: 1200px) and (max-width: 1919px) {
  .resume-preview, .resume-editor {
    font-size: 1rem;
    padding: 20px;
  }
}

.template-description {
  font-size: 0.75rem !important;
  line-height: 1.3 !important;
  white-space: normal !important;
  word-wrap: break-word !important;
  overflow: visible !important;
  text-overflow: unset !important;
  -webkit-line-clamp: unset !important;
  display: block !important;
  height: auto !important;
  max-height: none !important;
  padding: 8px 12px !important;
}

@media (max-width: 675px) {
  .template-description {
    font-size: 0.7rem !important;
    padding: 6px 8px !important;
  }
}
</style>
