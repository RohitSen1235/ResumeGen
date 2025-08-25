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
            Resume Preview
            <v-btn
              color="orange-lighten-2"
              variant="flat"
              :prepend-icon="isEditing ? 'mdi-content-save' : 'mdi-pencil'"
              @click="handleEditSave"
            >
              {{ isEditing ? 'Save' : 'Edit' }}
            </v-btn>
          </v-card-title>

          <v-card-text class="overflow-y-auto flex-grow-1" style="max-height: calc(100vh - 240px);">
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
          </v-card-text>

          <v-card-actions class="pa-4">
            <v-alert v-if="showOverflowWarning" type="warning" variant="tonal" class="mr-4" density="compact">
              {{ overflowMessage }}
            </v-alert>
            <v-spacer></v-spacer>
            <div class="d-flex gap-3">
              <v-btn
                color="orange-lighten-2"
                variant="flat"
                prepend-icon="mdi-file-pdf-box"
                @click="downloadPdf"
                :loading="pdfLoading"
                size="large"
              >
                Download PDF
              </v-btn>
              <v-btn
                color="orange-lighten-2"
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

const resumeStore = useResumeStore()
const auth = useAuthStore()
const route = useRoute()

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
const generatedResume = computed(() => resumeStore.result?.content || '')

// Payment dialog
const paymentDialog = ref(false)
const lastGeneratedFile = ref('')

// Initialize editable content when store content changes
const initializeEditableContent = () => {
  editableContent.value = generatedResume.value
}

const handleEditSave = async () => {
  if (isEditing.value) {
    try {
      console.log('Saving resume content:', editableContent.value)
      // Get resume ID from route params or store
      // Ensure we get a string ID (handle case where route.params.id might be an array)
      const routeId = Array.isArray(route.params.id) ? route.params.id[0] : route.params.id
      const resumeId = routeId || resumeStore.jobId
      await resumeStore.updateResumeContent(editableContent.value, resumeId as string)
      console.log('Resume content saved to store:', resumeStore.result?.content)
      isEditing.value = false
    } catch (error) {
      console.error('Failed to save resume content:', error)
    }
  } else {
    // Initialize editable content when entering edit mode
    initializeEditableContent()
    isEditing.value = true
  }
}

const formattedResumeContent = computed(() => {
  return marked(generatedResume.value, { breaks: true })
})

const checkCredits = async () => {
  try {
    await auth.fetchUser() // Refresh user data to get latest credits
    return (auth.user?.credits || 0) > 0
  } catch (error) {
    console.error('Error checking credits:', error)
    return false
  }
}

const showOverflowWarning = ref(false)
const overflowMessage = ref('')

const downloadPdf = async () => {
  if (!generatedResume.value) {
    console.error('No resume content to download')
    return
  }
  
    console.log('Current store content:', resumeStore.result?.content)
    console.log('Generated resume content:', generatedResume.value)
    
    try {
      pdfLoading.value = true
      showOverflowWarning.value = false
      console.log('Starting PDF generation with template:', selectedTemplate.value)
      console.log('Using backend URL:', import.meta.env.VITE_BACKEND_URL)
      
      const response = await apiClient.post('/generate-pdf', {
        ai_content: generatedResume.value,
        job_title: resumeStore.result?.job_title,
        agent_outputs: resumeStore.result?.agent_outputs,
        template_id: selectedTemplate.value
      })
    
    console.log('PDF generation response:', response.data)
    
    // Check for overflow warning
    if (response.data.overflow) {
      showOverflowWarning.value = true
      overflowMessage.value = response.data.message || 'either Edit and shorten the content to fit in single page or select a different template'
    }
    
    lastGeneratedFile.value = response.data.pdf_url
    
    // Download the PDF
    const pdfResponse = await apiClient.get(response.data.pdf_url, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([pdfResponse.data]))
    const link = document.createElement('a')
    link.href = url
    const filename = resumeStore.result?.job_title ?
      `resume-${resumeStore.result.job_title}-${new Date().toISOString().split('T')[0]}.pdf` :
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
        job_title: resumeStore.result?.job_title
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
    const filename = resumeStore.result?.job_title ?
      `resume-${resumeStore.result.job_title}-${new Date().toISOString().split('T')[0]}.docx` :
      `resume-${new Date().toISOString().split('T')[0]}.docx`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error: any) {
    console.error('Error generating/downloading Word document:', error)
  } finally {
    docxLoading.value = false
  }
}

const onPaymentCompleted = async () => {
  // Refresh user data to get updated credits
  await auth.fetchUser()
  paymentDialog.value = false
  
  // Optionally retry the last download action
  console.log('Payment completed, credits updated')
}

onMounted(async () => {
  await resumeStore.fetchTemplates();
  availableTemplates.value = resumeStore.templates;

  // Load template preview images with exact filenames
  availableTemplates.value.forEach((template: any) => {
    templatePreviews.value[template.id] = template.image_path;
  });

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
