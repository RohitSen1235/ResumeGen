<template>
  <v-container class="fill-height pa-0" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row no-gutters class="fill-height">
      <!-- Left Column - Form Inputs -->
      <v-col cols="12" lg="7" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-md-8 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="text-h4 font-weight-bold mb-4 text-center text-grey-darken-3">
            <img 
              src="@/assets/logo-dark.svg" 
              alt="Resume-Genie.ai" 
              class="mb-4"
              style="width: 220px; height: auto;"
            >
          </v-card-title>

          <v-card-subtitle class="text-body-1 mb-8 text-center text-grey-darken-1">
            Craft a winning resume with the power of AI
          </v-card-subtitle>

          <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 280px);">
              <v-alert
                color="primary"
                variant="flat"
                class="mb-8"
                border="start"
                elevation="4"
                rounded="lg"
              >
                <template v-slot:prepend>
                  <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
                </template>
                Provide the job description, and our AI will generate a resume tailored to it.
              </v-alert>

              <v-tabs 
                v-model="activeTab" 
                class="mb-6"
                color="primary"
                grow
                height="60"
                slider-color="primary"
              >
                <v-tab value="text" class="text-subtitle-1 font-weight-medium">
                  <v-icon icon="mdi-clipboard-text-outline" class="mr-2"></v-icon>
                  Paste Text
                </v-tab>
                <v-tab value="file" class="text-subtitle-1 font-weight-medium">
                  <v-icon icon="mdi-upload-outline" class="mr-2"></v-icon>
                  Upload File
                </v-tab>
              </v-tabs>

              <v-window v-model="activeTab">
                <v-window-item value="file">
                  <DragDropFileUpload
                    v-model="file"
                    accept=".txt"
                    :max-size="10"
                    :loading="resumeStore.isGenerating"
                    :error-message="errorMessage"
                    @error="handleFileError"
                    @file-selected="clearError"
                    @file-content-read="handleFileContentRead"
                    class="mb-4"
                  />
                </v-window-item>

                <v-window-item value="text">
                  <v-hover v-slot="{ isHovering, props }">
                    <v-textarea
                      v-bind="props"
                      v-model="resumeStore.jobDescriptionText"
                      :rules="[v => !!v || (activeTab === 'text' && 'Job description text is required')]"
                      label="Job Description"
                      placeholder="Paste the full job description here..."
                      :error-messages="errorMessage"
                      @update:model-value="clearError"
                      variant="outlined"
                      rows="8"
                      class="mb-4"
                      :class="{ 'elevation-6': isHovering }"
                      density="comfortable"
                      persistent-hint
                    >
                       <template v-slot:prepend-inner>
                        <v-icon icon="mdi-format-align-left" color="primary" class="mr-2"></v-icon>
                      </template>
                    </v-textarea>
                  </v-hover>
                </v-window-item>
              </v-window>

              <v-tooltip
                location="top"
                text="Let's create your new resume!"
              >
                <template v-slot:activator="{ props }">
                    <v-btn
                      v-bind="props"
                      color="orange-lighten-2"
                      size="x-large"
                      block
                      :loading="isLoading"
                      :disabled="!isInputValid"
                      @click="generateResume"
                      class="mt-6 elevation-4"
                      rounded="lg"
                    >
                    <template v-slot:prepend>
                      <v-icon icon="mdi-auto-fix"></v-icon>
                    </template>
                    {{ isLoading ? 'Generating...' : 'Generate Resume' }}
                  </v-btn>
                </template>
              </v-tooltip>

          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Column - Real-time Updates -->
      <v-col cols="12" lg="5" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-md-6 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 140px);">
            <div v-if="isGenerationInitiated || resumeStore.isGenerating || resumeStore.isCompleted || resumeStore.isFailed">
              <v-tabs 
                v-model="rightPanelTab" 
                color="primary"
                grow
                density="comfortable"
                class="mb-4"
              >
                <v-tab value="progress" class="text-subtitle-2">
                  <v-icon icon="mdi-progress-clock" class="mr-2"></v-icon>
                  Progress
                </v-tab>
                <v-tab 
                  value="analysis" 
                  class="text-subtitle-2"
                  :disabled="!resumeStore.isCompleted || !agentOutputs"
                >
                  <v-icon icon="mdi-chart-bell-curve-cumulative" class="mr-2"></v-icon>
                  Analysis
                </v-tab>
              </v-tabs>

              <v-window v-model="rightPanelTab" class="mt-4">
                <v-window-item value="progress">
                  <ProgressTracker />
                  <v-expand-transition>
                    <v-btn
                      v-if="resumeStore.isCompleted"
                      color="orange-lighten-2"
                      size="large"
                      block
                      prepend-icon="mdi-file-eye-outline"
                      @click="$router.push('/review-download')"
                      class="mt-6 elevation-4"
                      rounded="lg"
                    >
                      Review & Download
                    </v-btn>
                  </v-expand-transition>
                </v-window-item>
                
                <v-window-item value="analysis">
                  <ResumeAnalysis 
                    :agent-outputs="agentOutputs"
                    :analysis-summary="resumeStore.result?.analysis_summary"
                  />
                </v-window-item>
              </v-window>
            </div>

            <v-card 
              v-else
              variant="tonal" 
              class="text-center pa-8 d-flex flex-column justify-center align-center fill-height"
              color="primary"
              rounded="lg"
            >
              <v-icon icon="mdi-rocket-launch-outline" size="80" class="mb-6"></v-icon>
              <h3 class="text-h5 font-weight-medium mb-2">Ready to Generate</h3>
              <p class="text-body-1">
                Your personalized resume is just a click away.
              </p>
            </v-card>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Skills Selection Dialog -->
    <v-dialog v-model="showSkillsDialog" max-width="550">
      <v-card rounded="lg">
        <v-card-title class="text-h5 font-weight-medium bg-primary text-white pa-5">
          <v-icon icon="mdi-star-cog-outline" class="mr-3"></v-icon>
          Select Your Skills
        </v-card-title>
        <v-card-text class="pa-5">
          <p class="text-body-1 mb-4">Select the skills you want to highlight in your resume.</p>
          <v-list v-if="parsedSkills.length">
            <v-list-item
              v-for="skill in parsedSkills"
              :key="skill"
              class="pa-0"
            >
              <v-checkbox
                v-model="selectedSkills"
                :label="skill"
                :value="skill"
                color="primary"
                hide-details
              ></v-checkbox>
            </v-list-item>
          </v-list>
          <div v-else class="text-center text-grey-darken-1 mt-4">No skills found in your profile.</div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="flat" @click="showSkillsDialog = false" size="large">
            Apply Skills
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>


  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, type Ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import { useResumeStore } from '@/store/resume'
import ProgressTracker from './ProgressTracker.vue'
import OptimizationPreview from './OptimizationPreview.vue'
import ResumeAnalysis from './ResumeAnalysis.vue'
import DragDropFileUpload from './DragDropFileUpload.vue'

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
// Use resumeStore.jobDescriptionText directly
const generatedResume = ref('')
const agentOutputs = ref('')
const errorMessage: Ref<string> = ref('') // Explicitly type as string
const jobTitle = ref('')
const pdfUrl = ref<string | null>(null)
const docxUrl = ref<string | null>(null)
const pdfLoading = ref(false)
const docxLoading = ref(false)
const showSkillsDialog = ref(false)
const parsedSkills = ref<string[]>([])
const selectedSkills = ref<string[]>([])
const isEditing = ref(false)
const isLoading = ref(false)
const isGenerationInitiated = ref(false)

const formattedResumeContent = computed(() => {
  if (!generatedResume.value) return ''
  return marked(generatedResume.value, { breaks: true })
})

const formattedAgentOutputs = computed(() => {
  if (!agentOutputs.value) return ''
  return marked(agentOutputs.value, { breaks: true })
})

const isInputValid = computed(() => {
  return activeTab.value === 'file' ? !!file.value : !!resumeStore.jobDescriptionText?.trim()
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
  onMounted(async () => {
    await fetchTemplates()

    console.log('ResumeBuilder mounted. Current resumeStore state:', {
      jobId: resumeStore.jobId,
      isGenerating: resumeStore.isGenerating,
      isCompleted: resumeStore.isCompleted,
      isFailed: resumeStore.isFailed,
      status: resumeStore.status,
      result: resumeStore.result
    })

    // Restore state if a job was in progress and not completed/failed
    if (resumeStore.jobId && !resumeStore.isCompleted && !resumeStore.isFailed) {
      isLoading.value = true // Set loading if resuming
      isGenerationInitiated.value = true // Show progress tracker if resuming
      rightPanelTab.value = 'progress' // Ensure progress tab is active
      resumeStore.restoreGenerationState() // Restore timer and polling
      console.log('Restoring generation state for job:', resumeStore.jobId)
    } else if (resumeStore.isCompleted && resumeStore.result) {
      // If already completed, populate results immediately
      generatedResume.value = resumeStore.result.content
      agentOutputs.value = resumeStore.result.agent_outputs || ''
      jobTitle.value = resumeStore.result.job_title || ''
      pdfUrl.value = null
      docxUrl.value = null
      viewTab.value = 'preview'
      rightPanelTab.value = 'progress' // Show progress/analysis tab
      errorMessage.value = ''
      console.log('Job already completed on mount, populating data.')
    } else if (resumeStore.isFailed) {
      errorMessage.value = resumeStore.error || 'Resume generation failed'
      rightPanelTab.value = 'progress' // Show progress/analysis tab
      console.log('Job already failed on mount, showing error.')
    }

    // Set active tab based on whether jobDescriptionText exists in store
    if (resumeStore.jobDescriptionText) {
      activeTab.value = 'text';
    }
  })

const clearError = () => {
  errorMessage.value = ''
}

const handleFileError = (message: string) => {
  errorMessage.value = message
}

const handleFileContentRead = (content: string) => {
  resumeStore.jobDescriptionText = content;
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

const checkCredits = async () => {
  try {
    await auth.fetchUser() // Refresh user data to get latest credits
    return (auth.user?.credits || 0) > 0
  } catch (error) {
    console.error('Error checking credits:', error)
    return false
  }
}

const generateResume = async (): Promise<void> => {
  // Set loading and initiated states immediately
  isLoading.value = true
  isGenerationInitiated.value = true
  console.log('Generate Resume clicked - isLoading and isGenerationInitiated set to true')
  
  if (!auth.user?.profile) {
    errorMessage.value = 'Please complete your profile first'
    isLoading.value = false
    return
  }

  if (activeTab.value === 'file' && !file.value) {
    errorMessage.value = 'Please select a job description file'
    isLoading.value = false
    return
  }

  if (activeTab.value === 'text' && !resumeStore.jobDescriptionText?.trim()) {
    errorMessage.value = 'Please enter the job description text'
    isLoading.value = false
    return
  }

  // Check if user has credits before starting generation
  const hasCredits = await checkCredits()
  if (!hasCredits) {
    errorMessage.value = `Sorry ${auth.user?.profile?.name || ''}, you don't have enough credits. Please purchase credits to generate a resume.`
    isLoading.value = false
    return
  }

  clearError()

  try {
    // Create job description file
    let jobDescFile: File
    if (activeTab.value === 'file') {
      jobDescFile = file.value!
    } else {
      jobDescFile = new File([resumeStore.jobDescriptionText || ''], 'job_description.txt', { type: 'text/plain' })
    }

    // Start the new generation process
    await resumeStore.startGeneration(
      jobDescFile,
      selectedSkills.value.length > 0 ? selectedSkills.value : undefined,
      selectedTemplate.value
    )
    console.log('Resume generation started successfully')
  } catch (error: any) {
    errorMessage.value = error.message || 'Error starting resume generation. Please try again.'
    console.error('Error:', error)
    isLoading.value = false
  }
}

// Watch for changes in resumeStore.status to handle completion
watch(() => resumeStore.status?.status, (newStatus, oldStatus) => {
  console.log('Watch: resumeStore.status.status changed from', oldStatus, 'to', newStatus)
  
  if (newStatus === 'completed') {
    console.log('Status is completed, turning off loading')
    isLoading.value = false
    isGenerationInitiated.value = true // Keep it visible until user navigates away
    
    // Populate local state if result is available
    if (resumeStore.result) {
      generatedResume.value = resumeStore.result.content
      agentOutputs.value = resumeStore.result.agent_outputs || ''
      jobTitle.value = resumeStore.result.job_title || ''
      pdfUrl.value = null
      docxUrl.value = null
      viewTab.value = 'preview'
      errorMessage.value = ''
    }
  } else if (newStatus === 'failed') {
    console.log('Status is failed, turning off loading')
    isLoading.value = false
    isGenerationInitiated.value = true // Keep it visible to show the error
    errorMessage.value = resumeStore.error || 'Resume generation failed'
  }
})

// Watch for changes in resumeStore.isCompleted and resumeStore.isFailed as backup
watch(() => resumeStore.isCompleted, (newVal) => {
  console.log('Watch: resumeStore.isCompleted changed to', newVal, 'result:', resumeStore.result)
  if (newVal && resumeStore.result) {
    console.log('Generation completed via watch, updating local state and turning off loading')
    generatedResume.value = resumeStore.result.content
    agentOutputs.value = resumeStore.result.agent_outputs || ''
    jobTitle.value = resumeStore.result.job_title || ''
    pdfUrl.value = null
    docxUrl.value = null
    viewTab.value = 'preview'
    errorMessage.value = ''
    isLoading.value = false // Turn off loading when completed
    console.log('Loading state set to false, isLoading.value:', isLoading.value)
  }
})

watch(() => resumeStore.isFailed, (newVal) => {
  console.log('Watch: resumeStore.isFailed changed to', newVal, 'error:', resumeStore.error)
  if (newVal) {
    console.log('Generation failed via watch, turning off loading')
    errorMessage.value = resumeStore.error || 'Resume generation failed'
    isLoading.value = false // Turn off loading when failed
    console.log('Loading state set to false, isLoading.value:', isLoading.value)
  }
})

// Additional watch to ensure loading stops when generation is no longer active
watch(() => resumeStore.isGenerating, (newVal) => {
  console.log('Watch: resumeStore.isGenerating changed to', newVal)
  if (!newVal && (resumeStore.isCompleted || resumeStore.isFailed)) {
    console.log('Generation no longer active and completed/failed, ensuring loading is off')
    isLoading.value = false
  }
})

// Watch for changes in resumeStore.result to update local state
watch(() => resumeStore.result, (newResult) => {
  console.log('Watch: resumeStore.result changed to', newResult)
  if (newResult) {
    console.log('Resume result updated via watch, populating local state')
    generatedResume.value = newResult.content
    agentOutputs.value = newResult.agent_outputs || ''
    jobTitle.value = newResult.job_title || ''
    pdfUrl.value = null
    docxUrl.value = null
    viewTab.value = 'preview'
    errorMessage.value = ''
    
    // If result is available and status is completed, ensure loading is off
    if (resumeStore.isCompleted) {
      isLoading.value = false
      console.log('Result available and completed, ensuring loading is off')
    }
  }
}, { immediate: true }) // Run immediately on mount if result is already there

// Cleanup on component unmount
onUnmounted(() => {
  resumeStore.cleanup()
})
</script>
<style scoped>
.fill-height {
  min-height: 100vh;
}

.v-card {
  transition: all 0.3s ease-in-out;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
  font-weight: 600;
}

.v-tab {
  transition: background-color 0.3s ease;
}

.v-tab:hover {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

:deep(.v-field) {
  border-radius: 12px;
}

:deep(.v-field--variant-outlined .v-field__outline__start) {
  border-radius: 12px 0 0 12px !important;
}

:deep(.v-field--variant-outlined .v-field__outline__end) {
  border-radius: 0 12px 12px 0 !important;
}

.v-alert {
  border-radius: 12px;
}

@media (max-width: 1279px) {
  .v-col {
    padding: 12px !important;
  }
}
</style>
