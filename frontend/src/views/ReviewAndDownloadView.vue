<template>
  <v-container class="fill-height pa-0" fluid>
    <v-row no-gutters class="fill-height">
      <!-- Left Column - Template Selection -->
      <v-col cols="12" lg="6" class="pa-2 pa-sm-4">
        <v-card class="h-100 pa-6" elevation="8" rounded="lg">
          <v-card-title class="text-h4 mb-4">
            Select Template
          </v-card-title>

          <!-- Template Selection Carousel -->
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
              ></v-btn>
            </template>
            <template v-slot:next="{ props }">
              <v-btn
                v-bind="props"
                icon="mdi-chevron-right"
                variant="text"
                :disabled="loadingTemplates"
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
                    style="object-fit: contain; border-radius: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
                  ></v-img>
                </div>
                <v-card-title 
                  class="text-center pt-3"
                  :class="$vuetify.display.mobile ? 'text-body-1' : 'text-h6'"
                >
                  {{ template.name }}
                </v-card-title>
                <v-card-subtitle 
                  class="text-center pb-2"
                  :class="$vuetify.display.mobile ? 'text-caption' : 'text-body-2'"
                >
                  {{ template.description }}
                </v-card-subtitle>
              </v-card>
            </v-carousel-item>
          </v-carousel>
        </v-card>
      </v-col>

      <!-- Right Column - Resume Preview -->
      <v-col cols="12" lg="6" class="pa-2 pa-sm-4">
        <v-card class="h-100 pa-6" elevation="8" rounded="lg">
          <v-card-title class="text-h4 mb-4">
            Resume Preview
          </v-card-title>

          <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 200px);">
            <v-btn
              color="orange-lighten-2"
              variant="tonal"
              prepend-icon="mdi-pencil"
              @click="isEditing = !isEditing"
              class="mb-4"
            >
              {{ isEditing ? 'Save' : 'Edit' }}
            </v-btn>

            <v-textarea
              v-if="isEditing"
              v-model="generatedResume"
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

            <v-divider class="my-4"></v-divider>

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
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useResumeStore } from '@/store/resume'
import { useAuthStore } from '@/store/auth'
import axios from 'axios'
import { marked } from 'marked'

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
const generatedResume = computed(() => resumeStore.state.result?.content || '')
const formattedResumeContent = computed(() => {
  return marked(generatedResume.value, { breaks: true })
})

const fetchTemplates = async () => {
  try {
    loadingTemplates.value = true
    console.log('Fetching templates from:', `${import.meta.env.VITE_BACKEND_URL}/templates`)
    
    const response = await apiClient.get('/templates')
    console.log('Templates response:', response.data)
    
    if (response.data?.templates?.length) {
      availableTemplates.value = response.data.templates
      console.log('Available templates:', availableTemplates.value)
      
      // Load template preview images with exact filenames
      templatePreviews.value = {
        professional: `/template-previews/template_Professional.png`,
        modern: `/template-previews/template_Modern.png`,
        executive: `/template-previews/template_Executive.png`,
        classic: `/template-previews/template_Classic.png`,
        compact: `/template-previews/template_Compact.png`,
        dense: `/template-previews/template_Dense.png`,
        elegant: `/template-previews/template_Elegant.png`
      }
      console.log('Template preview URLs:', templatePreviews.value)
      
      // Set default template if available
      const defaultTemplate = response.data.templates.find((t: any) => t.is_default)
      if (defaultTemplate) {
        selectedTemplate.value = defaultTemplate.id
      }
    } else {
      console.warn('No templates found in response')
    }
  } catch (error) {
    console.error('Error fetching templates:', error)
  } finally {
    loadingTemplates.value = false
  }
}

const downloadPdf = async () => {
  if (!generatedResume.value) {
    console.error('No resume content to download')
    return
  }
  
  try {
    pdfLoading.value = true
    console.log('Starting PDF generation with template:', selectedTemplate.value)
    console.log('Using backend URL:', import.meta.env.VITE_BACKEND_URL)
    
    const response = await apiClient.post('/generate-pdf', {
      ai_content: generatedResume.value,
      job_title: resumeStore.state.result?.job_title,
      agent_outputs: resumeStore.state.result?.agent_outputs,
      template_id: selectedTemplate.value
    })
    
    console.log('PDF generation response:', response.data)
    
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
    console.error('Error details:', error.response?.data)
  } finally {
    pdfLoading.value = false
  }
}

const downloadDocx = async () => {
  if (!generatedResume.value) {
    console.error('No resume content to download')
    return
  }
  
  try {
    docxLoading.value = true
    console.log('Starting DOCX generation')
    const response = await axios.post('/api/generate-resume-docx', {
      ai_content: generatedResume.value,
      job_title: resumeStore.state.result?.job_title
    }, {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    // Download the DOCX
    const docxResponse = await axios.get(response.data.docx_url, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
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
  } catch (error) {
    console.error('Error generating/downloading Word document:', error)
  } finally {
    docxLoading.value = false
  }
}

onMounted(() => {
  fetchTemplates()
})
</script>

<style scoped>
/* Copy relevant styles from ResumeBuilder.vue */
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
  padding: 16px;
  max-height: 600px;
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
  font-size: 0.95rem;
}

.resume-editor {
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  padding: 16px;
  line-height: 1.6;
  font-size: 0.95rem;
  width: 100%;
  min-height: 600px;
}

@media (max-width: 675px) {
  .resume-preview, .resume-editor {
    max-height: 400px;
    padding: 8px;
    font-size: 0.8rem;
  }
}
</style>
