<template>
<v-container class="fill-height pa-0" fluid>
  <v-row no-gutters class="fill-height">
    <!-- Left Column - Form Inputs -->
    <v-col cols="12" lg="7" class="pa-2 pa-sm-4">
      <v-card class="h-100 pa-6" elevation="8" rounded="lg">
        <v-card-title class="text-h4 mb-4 d-flex align-center justify-center">
          <img 
            src="@/assets/logo-dark.svg" 
            alt="Resume-Genie.ai" 
            class="mb-2 mb-sm-4"
            :style="{
              width: $vuetify.display.mobile ? '140px' : '200px',
              height: 'auto'
            }"
          >
        </v-card-title>

        <v-card-subtitle class="text-body-2 text-sm-body-1 mb-4 mb-sm-6 text-center">
          Generate tailored, ATS-optimized resumes using advanced AI technology
        </v-card-subtitle>

        <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 200px);">
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

            <v-tooltip
              location="top"
              text="Generate an ATS-optimized resume based on the job description"
            >
              <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    color="orange-lighten-2"
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

            <v-expand-transition>
              <v-btn
                v-if="resumeStore.isCompleted"
                color="orange-lighten-2"
                variant="tonal"
                prepend-icon="mdi-eye"
                @click="$router.push('/review-download')"
                class="mt-4"
                block
              >
                Review & Download
              </v-btn>
            </v-expand-transition>

          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Column - Real-time Updates -->
      <v-col cols="12" lg="5" class="pa-1 pa-sm-2">
        <v-card class="h-100 pa-3" elevation="8" rounded="lg">
          <!-- <v-card-title class="text-body-1 mb-2 d-flex align-center justify-center pa-2">
            <v-icon icon="mdi-monitor-dashboard" size="small" class="mr-1"></v-icon>
            Real-time Updates
          </v-card-title> -->

          <v-card-text class="overflow-y-auto pa-2" style="max-height: calc(100vh - 150px);">
            <!-- Show tabs when generation is active or completed -->
            <div v-if="resumeStore.isGenerating || resumeStore.isCompleted || resumeStore.isFailed">
              <v-tabs 
                v-model="rightPanelTab" 
                color="primary"
                grow
                density="compact"
                class="mb-2"
              >
                <v-tab value="progress" class="text-body-2">
                  <v-icon icon="mdi-progress-clock" size="small" class="mr-1"></v-icon>
                  Progress
                </v-tab>
                <v-tab 
                  value="analysis" 
                  class="text-body-2"
                  :disabled="!resumeStore.isCompleted || !agentOutputs"
                >
                  <v-icon icon="mdi-chart-line" size="small" class="mr-1"></v-icon>
                  Analysis
                </v-tab>
              </v-tabs>

              <v-window v-model="rightPanelTab" class="mt-2">
                <v-window-item value="progress">
                  <ProgressTracker />
                </v-window-item>
                
                <v-window-item value="analysis">
                  <ResumeAnalysis 
                    :agent-outputs="agentOutputs"
                    :analysis-summary="resumeStore.state.result?.analysis_summary"
                  />
                </v-window-item>
              </v-window>
            </div>

            <!-- Placeholder when no generation is active -->
            <v-card 
              v-else
              variant="outlined" 
              class="text-center pa-4"
              density="compact"
            >
              <v-icon icon="mdi-rocket-launch" size="48" color="primary" class="mb-2"></v-icon>
              <v-card-title class="text-body-2 mb-1">Ready to Generate</v-card-title>
              <v-card-text class="text-caption">
                Fill in the job description and click "Generate Resume".
              </v-card-text>
            </v-card>
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
          <v-btn color="orange-lighten-2" variant="tonal" @click="showSkillsDialog = false">
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
import ResumeAnalysis from './ResumeAnalysis.vue'

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
const rightPanelTab = ref('progress')
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
        
        // Switch to analysis tab if analysis data is available
        if (agentOutputs.value) {
          rightPanelTab.value = 'analysis'
        }
        
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
/* Two-column layout styles */
.fill-height {
  min-height: 100vh;
}

/* Mobile-first responsive styles */
@media (max-width: 1279px) {
  /* Stack columns vertically on smaller screens */
  .v-row .v-col:nth-child(2) {
    order: 2;
  }
}

@media (min-width: 1280px) {
  /* Side-by-side layout on large screens */
  .v-row {
    height: 100vh;
  }
  
  .v-col {
    height: 100%;
  }
  
  /* 70/30 split for large screens */
  .v-col[class*="lg-8"] {
    flex: 0 0 70%;
    max-width: 70%;
  }
  
  .v-col[class*="lg-4"] {
    flex: 0 0 30%;
    max-width: 30%;
  }
}

/* Compact styles for real-time updates */
.compact-updates {
  font-size: 0.8rem;
}

.compact-updates .v-card-title {
  font-size: 0.75rem !important;
  padding: 8px !important;
}

.compact-updates .v-card-text {
  padding: 8px !important;
  font-size: 0.7rem;
}

.compact-updates .v-icon {
  font-size: 14px !important;
}

/* Compact card styles for right column */
.compact-card {
  font-size: 0.7rem;
}

.compact-card .v-card-title {
  font-size: 0.65rem !important;
  padding: 4px 8px !important;
  min-height: 24px !important;
  line-height: 1.2 !important;
}

.compact-content {
  font-size: 0.65rem !important;
  padding: 4px !important;
}

.compact-content :deep(*) {
  font-size: 0.65rem !important;
}

.compact-content :deep(.v-icon) {
  font-size: 12px !important;
}

.compact-content :deep(.v-card-title) {
  font-size: 0.6rem !important;
  padding: 2px 4px !important;
}

.compact-content :deep(.v-card-text) {
  font-size: 0.6rem !important;
  padding: 2px 4px !important;
  line-height: 1.1 !important;
}

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
