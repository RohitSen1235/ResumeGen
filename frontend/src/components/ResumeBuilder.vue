<template>
<v-container class="fill-height pa-0" fluid>
  <v-row align="center" justify="center" class="ma-0">
    <v-col cols="12" sm="10" md="8" class="pa-2 pa-sm-4">
        <v-card class="mx-auto pa-6" elevation="8" rounded="lg">
          <v-card-title class="text-h4 mb-4 d-flex align-center justify-center">
            <img 
              src="@/assets/logo-dark.svg" 
              alt="Resume-Genie.ai" 
              class="mb-2 mb-sm-4"
              :style="{
                width: $vuetify.display.mobile ? '140px' : '300px',
                height: 'auto'
              }"
            >
          </v-card-title>

          <v-card-subtitle class="text-body-2 text-sm-body-1 mb-4 mb-sm-6 text-center">
            Generate tailored, ATS-optimized resumes using advanced AI technology
          </v-card-subtitle>

          <v-card-text>
            <!-- Job Description Input -->
            <v-alert
              color="info"
              variant="tonal"
              class="mb-6"
              border="start"
              elevation="2"
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-information" class="mr-2"></v-icon>
              </template>
              Choose your preferred method to input the job description. Our AI will analyze it and generate a tailored, ATS-friendly resume.
            </v-alert>

            <v-tabs 
              v-model="activeTab" 
              class="mb-4 mb-sm-6"
              color="primary"
              grow
              :height="$vuetify.display.mobile ? 48 : 56"
            >
              <v-tab value="text" class="text-body-1">
                <v-icon icon="mdi-clipboard-text" class="mr-2"></v-icon>
                Job Description Text
              </v-tab>
              <v-tab value="file" class="text-body-1">
                <v-icon icon="mdi-file-upload" class="mr-2"></v-icon>
                Select File
              </v-tab>
            </v-tabs>

            <v-window v-model="activeTab">
              <v-window-item value="file">
                <v-hover v-slot="{ isHovering, props }">
                  <v-file-input
                    v-bind="props"
                    v-model="file"
                    :rules="[v => !!v || (activeTab === 'file' && 'Job description file is required')]"
                    accept=".txt,.pdf,.doc,.docx"
                    placeholder="Drag and drop a file or click to browse"
                    prepend-icon="mdi-file-document"
                    label="Browse and Add Job Description File"
                    :error-messages="errorMessage"
                    @update:model-value="clearError"
                    variant="outlined"
                    class="mb-4"
                    :class="{ 'elevation-3': isHovering }"
                    density="comfortable"
                    :hint="'Supported formats: .txt'"
                    persistent-hint
                  >
                    <template v-slot:prepend>
                      <v-tooltip location="top" text="Upload a job description file">
                        <template v-slot:activator="{ props }">
                        </template>
                      </v-tooltip>
                    </template>
                  </v-file-input>
                </v-hover>
              </v-window-item>

              <v-window-item value="text">
                <v-hover v-slot="{ isHovering, props }">
                  <v-textarea
                    v-bind="props"
                    v-model="jobDescriptionText"
                    :rules="[v => !!v || (activeTab === 'text' && 'Job description text is required')]"
                    label="Type Job Description Text"
                    placeholder="Paste the job description here"
                    :error-messages="errorMessage"
                    @update:model-value="clearError"
                    variant="outlined"
                    :rows="$vuetify.display.mobile ? 5 : 8"
                    class="mb-4"
                    :class="{ 'elevation-3': isHovering }"
                    density="comfortable"
                    :hint="'Copy and Paste the job description from any source (Linkedin , Naukri ...)'"
                    persistent-hint
                  >
                    <template v-slot:prepend>
                      <v-tooltip location="top" text="Paste job description text">
                        <template v-slot:activator="{ props }">
                          <v-icon v-bind="props" icon="mdi-clipboard-text" color="primary"></v-icon>
                        </template>
                      </v-tooltip>
                    </template>
                  </v-textarea>
                </v-hover>
              </v-window-item>
            </v-window>

            <!-- Template Selection Carousel -->
            <div class="mb-4">
              <v-carousel
                v-model="selectedTemplateIndex"
                :height="$vuetify.display.mobile ? 450 : $vuetify.display.smAndDown ? 550 : 650"
                show-arrows="hover"
                hide-delimiters
                class="template-carousel"
              >
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
            </div>

            <v-tooltip
              location="top"
              text="Generate an ATS-optimized resume based on the job description"
            >
              <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    color="primary"
                    :size="$vuetify.display.mobile ? 'default' : 'large'"
                    block
                    :loading="loading"
                    :disabled="!isInputValid"
                    @click="generateResume"
                    class="mt-4 elevation-2"
                    rounded="lg"
                  >
                  <template v-slot:prepend>
                    <v-icon icon="mdi-magic-staff"></v-icon>
                  </template>
                  {{ loading ? 'Generating Resume...' : 'Generate Resume' }}
                </v-btn>
              </template>
            </v-tooltip>

            <!-- Progress Tracking Section -->
            <v-expand-transition>
              <div v-if="resumeStore.isGenerating || resumeStore.isCompleted || resumeStore.isFailed" class="mt-4 mt-sm-6">
                <v-row>
                  <v-col cols="12" md="6">
                    <ProgressTracker />
                  </v-col>
                  <v-col cols="12" md="6">
                    <OptimizationPreview />
                  </v-col>
                </v-row>
              </div>
            </v-expand-transition>

            <!-- Resume Display Section -->
            <v-expand-transition>
                <v-card
                  v-if="generatedResume"
                  class="mt-4 mt-sm-6 resume-card"
                  variant="outlined"
                  elevation="3"
                  rounded="lg"
                  style="max-width: 100%; width: 100%; overflow-x: hidden;"
                >
                <v-card-title class="d-flex align-center pa-4 bg-primary text-white rounded-t-lg">
                  <v-icon icon="mdi-file-check" class="mr-2"></v-icon>
                  AI-Optimized Resume
                </v-card-title>
                
                <v-tabs v-model="viewTab" color="primary" grow :height="$vuetify.display.mobile ? 48 : 56">
                  <v-tab value="preview">
                    <v-icon icon="mdi-eye" class="mr-2"></v-icon>
                    Resume Preview
                  </v-tab>
                  <v-tab value="raw">
                    <v-icon icon="mdi-code-tags" class="mr-2"></v-icon>
                    Resume Analysis
                  </v-tab>
                </v-tabs>

                <v-divider></v-divider>

                <v-window v-model="viewTab" class="resume-container">
                  <v-window-item value="preview" class="resume-container">
                    <v-card-text class="mt-4 resume-container">
                      <v-btn
                        v-if="generatedResume"
                        color="primary"
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
                    </v-card-text>
                  </v-window-item>
                  
                  <v-window-item value="raw" class="resume-container">
                    <v-card-text class="mt-4 resume-container">
                      <div class="resume-content" v-html="formattedAgentOutputs"></div>
                    </v-card-text>
                  </v-window-item>
                </v-window>

                <v-divider></v-divider>

                <v-card-actions class="pa-4">
                  <div class="d-flex gap-2">
                    <v-tooltip location="top" text="Download professional PDF version">
                      <template v-slot:activator="{ props }">
                        <v-btn
                          v-if="generatedResume"
                          v-bind="props"
                          color="primary"
                          variant="tonal"
                          prepend-icon="mdi-file-pdf-box"
                          @click="downloadPdf"
                          :loading="pdfLoading"
                        >
                          Download PDF
                        </v-btn>
                      </template>
                    </v-tooltip>

                    <v-tooltip location="top" text="Download Word document version">
                      <template v-slot:activator="{ props }">
                        <v-btn
                          v-bind="props"
                          color="primary"
                          variant="tonal"
                          prepend-icon="mdi-file-word"
                          @click="downloadDocx"
                          :loading="docxLoading"
                          :disabled="!generatedResume"
                        >
                          Download Word
                        </v-btn>
                      </template>
                    </v-tooltip>
                  </div>

                  <v-spacer></v-spacer>
                </v-card-actions>
              </v-card>
            </v-expand-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Skills Selection Dialog -->
    <v-dialog v-model="showSkillsDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5 bg-primary text-white pa-4">
          <v-icon icon="mdi-tools" class="mr-2"></v-icon>
          Select Skills
        </v-card-title>
        <v-card-text class="pa-4">
          <v-list v-if="parsedSkills.length">
            <v-list-item
              v-for="skill in parsedSkills"
              :key="skill"
            >
              <v-list-item-title>
                <v-checkbox
                  v-model="selectedSkills"
                  :label="skill"
                  :value="skill"
                ></v-checkbox>
              </v-list-item-title>
            </v-list-item>
          </v-list>
          <div v-else>No skills found in the uploaded resume.</div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="tonal" @click="showSkillsDialog = false">
            Apply Skills
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import { useResumeStore } from '@/store/resume'
import ProgressTracker from './ProgressTracker.vue'
import OptimizationPreview from './OptimizationPreview.vue'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
})
import { marked } from 'marked'

const auth = useAuthStore()
const resumeStore = useResumeStore()

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

const activeTab = ref('text')
const viewTab = ref('preview')
const file = ref<File | null>(null)
const jobDescriptionText = ref('')
const loading = ref(false)
const generatedResume = ref('')
const agentOutputs = ref('')
const errorMessage = ref('')
const jobTitle = ref('')
const pdfUrl = ref<string | null>(null)
const docxUrl = ref<string | null>(null)
const pdfLoading = ref(false)
const docxLoading = ref(false)
const showSkillsDialog = ref(false)
const parsedSkills = ref<string[]>([])
const selectedSkills = ref<string[]>([])
const isEditing = ref(false)

const formattedResumeContent = computed(() => {
  if (!generatedResume.value) return ''
  return marked(generatedResume.value, { breaks: true })
})

const formattedAgentOutputs = computed(() => {
  if (!agentOutputs.value) return ''
  return marked(agentOutputs.value, { breaks: true })
})

const isInputValid = computed(() => {
  return activeTab.value === 'file' ? !!file.value : !!jobDescriptionText.value.trim()
})

const fetchTemplates = async () => {
  try {
    loadingTemplates.value = true
    const response = await apiClient.get('/templates', {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    availableTemplates.value = response.data.templates
    
    // Set default template from config
    const defaultTemplate = response.data.templates.find((t: {is_default: boolean}) => t.is_default)
    if (defaultTemplate) {
      selectedTemplate.value = defaultTemplate.id
    }
    
    // Load template preview images (4:3 aspect ratio recommended)
    templatePreviews.value = {
      professional: '/template-previews/template_Professional.png',
      modern: '/template-previews/template_Modern.png',
      executive: '/template-previews/template_Executive.png',
      classic: '/template-previews/template_Classic.png',
      compact: '/template-previews/template_Compact.png',
      dense: '/template-previews/template_Dense.png',
      elegant: '/template-previews/template_Elegant.png'
    }
  } catch (error) {
    console.error('Error fetching templates:', error)
    errorMessage.value = 'Error loading templates. Please try again.'
  } finally {
    loadingTemplates.value = false
  }
}

// Fetch templates on component mount
onMounted(() => {
  fetchTemplates()
})

const clearError = () => {
  errorMessage.value = ''
}

const downloadResume = () => {
  const blob = new Blob([generatedResume.value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const filename = jobTitle.value ? 
    `resume-${jobTitle.value}-${new Date().toISOString().split('T')[0]}.txt` : 
    `resume-${new Date().toISOString().split('T')[0]}.txt`
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

const downloadPdf = async () => {
    if (!generatedResume.value) return
    
    try {
        pdfLoading.value = true
        // First generate the PDF file
        const generateResponse = await apiClient.post('/generate-pdf', {
            ai_content: generatedResume.value,
            job_title: jobTitle.value,
            agent_outputs: agentOutputs.value,
            template_id: selectedTemplate.value
        }, {
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        })
        
        // Then download the generated PDF
        const downloadResponse = await apiClient.get(generateResponse.data.pdf_url, {
            responseType: 'blob',
            headers: {
                'Authorization': `Bearer ${auth.token}`
            }
        })
        
        const url = window.URL.createObjectURL(new Blob([downloadResponse.data]))
        const link = document.createElement('a')
        link.href = url
        const filename = jobTitle.value ?
            `resume-${jobTitle.value}-${new Date().toISOString().split('T')[0]}.pdf` :
            `resume-${new Date().toISOString().split('T')[0]}.pdf`
        link.setAttribute('download', filename)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (error) {
        console.error('Error generating/downloading PDF:', error)
        errorMessage.value = 'Error generating PDF. Please try again.'
    } finally {
        pdfLoading.value = false
    }
}

const downloadDocx = async () => {
  if (!generatedResume.value) return
  
  try {
    docxLoading.value = true
    // First generate the DOCX file
    const generateResponse = await apiClient.post('/generate-resume-docx', {
      ai_content: generatedResume.value,
      job_title: jobTitle.value
    }, {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    // Then download the generated DOCX
    const downloadResponse = await apiClient.get(generateResponse.data.docx_url, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    const url = window.URL.createObjectURL(new Blob([downloadResponse.data]))
    const link = document.createElement('a')
    link.href = url
    const filename = jobTitle.value ?
      `resume-${jobTitle.value}-${new Date().toISOString().split('T')[0]}.docx` :
      `resume-${new Date().toISOString().split('T')[0]}.docx`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error generating/downloading Word document:', error)
    errorMessage.value = 'Error generating Word document. Please try again.'
  } finally {
    docxLoading.value = false
  }
}

const generateResume = async (): Promise<void> => {
  if (!auth.user?.profile) {
    errorMessage.value = 'Please complete your profile first'
    return
  }

  if (activeTab.value === 'file' && !file.value) {
    errorMessage.value = 'Please select a job description file'
    return
  }

  if (activeTab.value === 'text' && !jobDescriptionText.value.trim()) {
    errorMessage.value = 'Please enter the job description text'
    return
  }

  loading.value = true
  clearError()

  try {
    // Create job description file
    let jobDescFile: File
    if (activeTab.value === 'file') {
      jobDescFile = file.value!
    } else {
      jobDescFile = new File([jobDescriptionText.value], 'job_description.txt', { type: 'text/plain' })
    }

    // Start the new generation process
    const jobId = await resumeStore.startGeneration(
      jobDescFile,
      selectedSkills.value.length > 0 ? selectedSkills.value : undefined,
      selectedTemplate.value
    )

    // Wait for completion
    const checkCompletion = () => {
      console.log('Checking completion:', {
        isCompleted: resumeStore.isCompleted,
        isFailed: resumeStore.isFailed,
        isGenerating: resumeStore.isGenerating,
        hasResult: !!resumeStore.state.result,
        status: resumeStore.state.status?.status
      })
      
      if (resumeStore.isCompleted && resumeStore.state.result) {
        console.log('Generation completed, updating local state')
        // Update local state with results
        generatedResume.value = resumeStore.state.result.content
        agentOutputs.value = resumeStore.state.result.agent_outputs || ''
        jobTitle.value = resumeStore.state.result.job_title || ''
        pdfUrl.value = null
        docxUrl.value = null
        viewTab.value = 'preview'
        loading.value = false
        
        // Clear any previous errors
        errorMessage.value = ''
        console.log('Local state updated, loading set to false')
        return // Stop checking
      } else if (resumeStore.isFailed) {
        console.log('Generation failed')
        errorMessage.value = resumeStore.state.error || 'Resume generation failed'
        loading.value = false
        return // Stop checking
      } else if (resumeStore.isGenerating || resumeStore.state.status) {
        // Continue checking
        setTimeout(checkCompletion, 1000)
      } else {
        // No status yet, keep checking
        setTimeout(checkCompletion, 1000)
      }
    }

    // Start checking for completion
    setTimeout(checkCompletion, 1000)

  } catch (error: any) {
    errorMessage.value = error.message || 'Error starting resume generation. Please try again.'
    console.error('Error:', error)
    loading.value = false
  }
}

// Cleanup on component unmount
onUnmounted(() => {
  resumeStore.cleanup()
})
</script>
<style scoped>
/* Mobile-first responsive styles */
@media (max-width: 675px) {
  .v-container {
    padding: 4px !important;
  }

  .v-col {
    padding: 4px !important;
  }

  .v-card {
    padding: 4px !important;
    margin: 0 !important;
    border-radius: 8px !important;
  }
  
  .v-card-title {
    font-size: 1.1rem !important;
    padding: 4px !important;
    margin-bottom: 8px !important;
  }

  .v-card-subtitle {
    font-size: 0.75rem !important;
    margin-bottom: 8px !important;
    padding: 0 4px !important;
  }

  img {
    max-width: 140px !important;
    height: auto !important;
  }

  .v-btn {
    font-size: 0.75rem !important;
    padding: 0 6px !important;
    min-width: auto !important;
    height: 32px !important;
  }

  .v-tabs {
    font-size: 0.65rem !important;
    height: 36px !important;
  }

  .v-tab {
    padding: 0 6px !important;
    min-width: auto !important;
  }

  .v-icon {
    font-size: 16px !important;
    margin-right: 2px !important;
  }

  .v-card-text {
    padding: 4px !important;
  }

  .v-textarea, .v-file-input {
    font-size: 0.75rem !important;
  }

  .v-alert {
    margin-bottom: 12px !important;
    font-size: 0.75rem !important;
  }

  .v-alert .v-icon {
    font-size: 16px !important;
  }

  /* Template carousel specific mobile styles */
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
}

/* Medium small screens - between 576px and 675px */
@media (max-width: 675px) and (min-width: 576px) {
  .template-carousel {
    height: 450px !important;
  }

  .template-image-container {
    height: 320px !important;
    width: 100% !important;
    overflow: hidden !important;
    padding: 6px !important;
    margin: 0 !important;
    background-color: #f5f5f5 !important;
    border-radius: 8px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
  }

  .template-preview {
    max-width: 85vw !important;
    max-height: 308px !important;
    width: auto !important;
    height: auto !important;
    object-fit: contain !important;
    object-position: center !important;
    border-radius: 4px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
  }
}

/* Extra small screens - below 575px */
@media (max-width: 575px) {
  .template-carousel {
    height: 400px !important;
  }

  .template-image-container {
    height: 280px !important;
    width: 100% !important;
    overflow: hidden !important;
    padding: 4px !important;
    margin: 0 !important;
    background-color: #f5f5f5 !important;
    border-radius: 8px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
  }

  .template-preview {
    max-width: 90vw !important;
    max-height: 272px !important;
    width: auto !important;
    height: auto !important;
    object-fit: contain !important;
    object-position: center !important;
    border-radius: 4px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
  }

  .v-carousel-item .v-card {
    padding: 4px !important;
  }

  .v-carousel-item .v-card-title {
    font-size: 0.9rem !important;
    padding: 8px 4px 4px 4px !important;
    margin-bottom: 4px !important;
  }

  .v-carousel-item .v-card-subtitle {
    font-size: 0.7rem !important;
    padding: 0 4px 8px 4px !important;
    line-height: 1.2 !important;
  }
}

/* Template preview specific styles for consistent sizing */
.template-image-container {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 8px;
  overflow: hidden;
}

.template-preview {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  object-fit: contain;
  object-position: center;
  transition: transform 0.2s ease-in-out;
}

.template-preview:hover {
  transform: scale(1.02);
}

/* Ensure all template images maintain aspect ratio */
.v-carousel-item .v-img {
  aspect-ratio: 0.707 !important;
}

/* Base styles for content containers */
.resume-content, .resume-preview {
  width: 100%;
  max-width: 100%;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  box-sizing: border-box;
}

/* Ensure consistent width for parent containers */
.v-container {
  width: 100% !important;
  max-width: 100% !important;
  padding: 8px !important;
}

.v-window,
.v-window-item,
.v-card,
.v-card-text {
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
  box-sizing: border-box !important;
}

/* Additional responsive fixes for intermediate screen sizes */
@media (max-width: 620px) {
  .v-col {
    padding: 2px !important;
    max-width: 100% !important;
  }
  
  .v-card {
    margin: 0 !important;
    padding: 8px !important;
    max-width: 100% !important;
    width: 100% !important;
  }
  
  .v-container {
    padding: 2px !important;
    margin: 0 !important;
  }
}

@media (max-width: 560px) {
  .v-row {
    margin: 0 !important;
    padding: 0 !important;
  }
  
  .v-col {
    padding: 0 !important;
    margin: 0 !important;
  }
  
  .v-card {
    margin: 0 !important;
    padding: 4px !important;
    border-radius: 4px !important;
  }
  
  .v-container {
    padding: 0 !important;
    margin: 0 !important;
  }
}

@media (max-width: 675px) {
  .v-col {
    padding: 0 !important;
  }
  
  .v-card-text {
    padding: 4px !important;
  }
  
  .v-textarea, .v-file-input {
    font-size: 0.75rem !important;
    --v-field-padding-start: 6px !important;
  }

  .v-field__prepend-inner {
    padding-inline-end: 6px !important;
  }

  .v-card-actions {
    padding: 4px !important;
    flex-wrap: wrap !important;
  }

  .v-card-actions .d-flex {
    flex-wrap: wrap !important;
    gap: 4px !important;
  }

  .resume-card {
    margin: 8px 0 !important;
  }

  .resume-card .v-card-title {
    padding: 8px 4px !important;
    font-size: 1rem !important;
  }

  .resume-container {
    width: 100% !important;
    overflow-x: hidden !important;
  }
}

/* Specific styles for resume content and preview */
.resume-content, .resume-preview {
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  font-size: 0.95rem;
  width: 100%;
  overflow: auto;
}

@media (max-width: 675px) {
  .resume-content, .resume-preview {
    font-size: 0.8rem;
    padding: 6px;
    max-height: 300px;
    overflow-x: auto;
  }
  
  .resume-preview :deep(h1) {
    font-size: 1.1rem;
    margin-top: 0.8rem;
    margin-bottom: 0.8rem;
  }
  
  .resume-preview :deep(h2) {
    font-size: 1rem;
    margin-bottom: 0.6rem;
  }
  
  .resume-preview :deep(p),
  .resume-preview :deep(li) {
    font-size: 0.8rem;
    margin-bottom: 0.5rem;
  }
  
  .resume-preview :deep(ul) {
    padding-left: 0.8rem;
  }

  .resume-editor {
    font-size: 0.8rem;
    padding: 8px;
  }
}

/* Force all nested elements to respect container width */
.resume-preview :deep(*),
.resume-content :deep(*) {
  max-width: 100% !important;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  box-sizing: border-box;
}

.resume-preview :deep(table) {
  width: 100% !important;
  display: block;
  overflow-x: auto;
}

.resume-preview :deep(img) {
  max-width: 100% !important;
  height: auto !important;
}

/* Specific element styles in preview */
.resume-preview :deep(p),
.resume-preview :deep(div),
.resume-preview :deep(span) {
  margin: 0 0 1rem 0;
}

.resume-preview :deep(h1) {
  font-size: 1.5rem;
  color: rgb(var(--v-theme-primary));
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
}

.resume-preview :deep(ul) {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  max-width: calc(100% - 1.5rem);
}

.resume-preview :deep(li) {
  margin-bottom: 0.5rem;
}

/* Project section specific styles */
.resume-preview :deep(li strong) {
  color: rgb(var(--v-theme-primary));
  font-weight: 500;
}

.resume-preview :deep(li em) {
  color: rgba(var(--v-theme-on-surface), 0.7);
  font-style: italic;
}

.resume-editor {
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  padding: 16px;
  line-height: 1.6;
  font-size: 0.95rem;
}

/* Container constraints */
.v-window,
.v-window-item,
.v-card,
.v-card-text {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}

@media (max-width: 675px) {
  .resume-content, .resume-preview {
    max-height: 280px;
    padding: 8px;
    font-size: 0.8rem;
  }
  
  .v-dialog {
    width: 98% !important;
    margin: 4px !important;
    max-width: none !important;
  }

  .v-dialog .v-card {
    margin: 0 !important;
  }

  .v-dialog .v-card-text {
    padding: 8px !important;
  }
}

/* Additional UI styles */
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.v-file-input,
.v-textarea {
  transition: all 0.2s ease-in-out;
}

:deep(.v-field) {
  border-radius: 8px;
}

.v-card-title {
  letter-spacing: 0.5px;
}

.v-alert {
  border-radius: 8px;
}

</style>
