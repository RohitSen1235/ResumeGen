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

          <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 220px);">
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
                  <v-hover v-slot="{ isHovering, props }">
                    <v-file-input
                      v-bind="props"
                      v-model="file"
                      :rules="[v => !!v || (activeTab === 'file' && 'A job description file is required')]"
                      accept=".txt,.pdf,.doc,.docx"
                      placeholder="Drop a file here or click to upload"
                      prepend-icon=""
                      label="Job Description File"
                      :error-messages="errorMessage"
                      @update:model-value="clearError"
                      variant="outlined"
                      class="mb-4"
                      :class="{ 'elevation-6': isHovering }"
                      density="comfortable"
                      persistent-hint
                    >
                      <template v-slot:prepend-inner>
                        <v-icon icon="mdi-file-document-outline" color="primary" class="mr-2"></v-icon>
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
                      label="Job Description"
                      placeholder="Paste the full job description here..."
                      :error-messages="errorMessage"
                      @update:model-value="clearError"
                      variant="outlined"
                      rows="10"
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
                      color="primary"
                      size="x-large"
                      block
                      :loading="loading"
                      :disabled="!isInputValid"
                      @click="generateResume"
                      class="mt-6 elevation-4"
                      rounded="lg"
                    >
                    <template v-slot:prepend>
                      <v-icon icon="mdi-auto-fix"></v-icon>
                    </template>
                    {{ loading ? 'Generating...' : 'Generate Resume' }}
                  </v-btn>
                </template>
              </v-tooltip>

          </v-card-text>
        </v-card>
      </v-col>

      <!-- Right Column - Real-time Updates -->
      <v-col cols="12" lg="5" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-md-6 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 100px);">
            <div v-if="resumeStore.isGenerating || resumeStore.isCompleted || resumeStore.isFailed">
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
                      color="primary"
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
                    :analysis-summary="resumeStore.state.result?.analysis_summary"
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

    <!-- Payment Dialog -->
    <PaymentDialog 
      v-model="paymentDialog"
      :credits="auth.user?.credits || 0"
      :resume-file="''"
      @payment-completed="onPaymentCompleted"
    />

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
import PaymentDialog from './PaymentDialog.vue'

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

// Payment dialog
const paymentDialog = ref(false)

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

  // Check if user has credits before starting generation
  const hasCredits = await checkCredits()
  if (!hasCredits) {
    paymentDialog.value = true
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
        
        // Keep the progress tab active - user can manually switch to analysis
        
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
    if (error.message?.includes('credits') || error.message?.includes('402')) {
      // Payment required
      paymentDialog.value = true
    } else {
      errorMessage.value = error.message || 'Error starting resume generation. Please try again.'
    }
    console.error('Error:', error)
    loading.value = false
  }
}

const onPaymentCompleted = async () => {
  // Refresh user data to get updated credits
  await auth.fetchUser()
  paymentDialog.value = false
  
  // Optionally retry the generation
  console.log('Payment completed, credits updated')
}

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
