<template>
  <v-container class="fill-height pa-0" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row no-gutters class="fill-height">
      <!-- Left Column - Form Inputs -->
      <v-col cols="12" lg="7" class="d-flex flex-column pa-4">
        <v-card class="flex-grow-1 pa-md-8 pa-4" elevation="12" rounded="xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <div class="text-center mb-4">
            <img 
              src="@/assets/logo-dark.svg" 
              alt="Resume-Genie.ai" 
              style="width: 180px; height: auto;"
            >
            <p class="text-body-1 mt-2 text-grey-darken-1">
              Craft a winning resume with the power of AI
            </p>
          </div>

          <v-card-text class="overflow-y-auto" style="max-height: calc(100vh - 220px);">
            <v-alert
              color="primary"
              variant="tonal"
              class="mb-6"
              border="start"
              elevation="2"
              rounded="lg"
              density="compact"
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
              </template>
              Provide the job description, and our AI will generate a resume tailored to it.
            </v-alert>

            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="resumeStore.companyName"
                  label="Company Name"
                  placeholder="e.g., Google, Microsoft"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-domain"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="resumeStore.jobTitle"
                  label="Job Title"
                  placeholder="e.g., Software Engineer"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-briefcase-outline"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-row class="align-stretch">
              <v-col cols="12" md="9" class="d-flex">
                <v-textarea
                  v-model="resumeStore.jobDescriptionText"
                  label="Job Description"
                  placeholder="Paste the full job description here..."
                  variant="outlined"
                  rows="12"
                  class="flex-grow-1"
                  style="height: 380px;"
                  :error-messages="errorMessage"
                  @update:model-value="clearError"
                  persistent-hint
                ></v-textarea>
              </v-col>
              <v-col cols="12" md="3" class="d-flex">
                <DragDropFileUpload
                  v-model="file"
                  accept=".txt"
                  supported-formats="TXT"
                  :max-size="10"
                  :loading="resumeStore.isGenerating"
                  :error-messages="errorMessage"
                  @error="handleFileError"
                  @file-selected="clearError"
                  @file-content-read="handleFileContentRead"
                  class="flex-grow-1 drag-drop-fixed-height"
                />
              </v-col>
            </v-row>

            <v-btn
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
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, type Ref, defineAsyncComponent } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'
import { useResumeStore } from '@/store/resume'
import DragDropFileUpload from './DragDropFileUpload.vue'

const ProgressTracker = defineAsyncComponent(() => import('./ProgressTracker.vue'))
const ResumeAnalysis = defineAsyncComponent(() => import('./ResumeAnalysis.vue'))

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
})
import { marked } from 'marked'

const auth = useAuthStore()
const resumeStore = useResumeStore()

const rightPanelTab = ref('progress')
const file = ref<File | null>(null)
const generatedResume = ref('')
const agentOutputs = ref('')
const errorMessage: Ref<string> = ref('')
const isLoading = ref(false)
const isGenerationInitiated = ref(false)

const isInputValid = computed(() => {
  return (
    !!resumeStore.companyName?.trim() &&
    !!resumeStore.jobTitle?.trim() &&
    (!!resumeStore.jobDescriptionText?.trim() || !!file.value)
  )
})

onMounted(() => {
  if (resumeStore.jobId && !resumeStore.isCompleted && !resumeStore.isFailed) {
    isLoading.value = true
    isGenerationInitiated.value = true
    rightPanelTab.value = 'progress'
    resumeStore.restoreGenerationState()
  } else if (resumeStore.isCompleted && resumeStore.result) {
    generatedResume.value = resumeStore.result.content
    agentOutputs.value = resumeStore.result.agent_outputs || ''
    resumeStore.companyName = resumeStore.result.company_name || ''
    resumeStore.jobTitle = resumeStore.result.job_title || ''
    rightPanelTab.value = 'progress'
  } else if (resumeStore.isFailed) {
    errorMessage.value = resumeStore.error || 'Resume generation failed'
    rightPanelTab.value = 'progress'
  }
})

const clearError = () => {
  errorMessage.value = ''
}

const handleFileError = (message: string) => {
  errorMessage.value = message
}

const handleFileContentRead = (content: string) => {
  resumeStore.jobDescriptionText = content
  file.value = null // Clear the file input after reading
}

const generateResume = async (): Promise<void> => {
  isLoading.value = true
  isGenerationInitiated.value = true
  
  if (!auth.user?.profile) {
    errorMessage.value = 'Please complete your profile first'
    isLoading.value = false
    return
  }

  if (!resumeStore.jobDescriptionText?.trim() && !file.value) {
    errorMessage.value = 'Please provide the job description by pasting text or uploading a file.'
    isLoading.value = false
    return
  }

  const hasCredits = (auth.user?.credits || 0) > 0
  if (!hasCredits) {
    errorMessage.value = `Sorry ${auth.user?.profile?.name || ''}, you don't have enough credits.`
    isLoading.value = false
    return
  }

  clearError()

  try {
    let jobDescFile: File
    if (file.value) {
      jobDescFile = file.value
    } else {
      jobDescFile = new File([resumeStore.jobDescriptionText || ''], 'job_description.txt', { type: 'text/plain' })
    }

    await resumeStore.startGeneration(
      jobDescFile,
      resumeStore.companyName || '',
      resumeStore.jobTitle || ''
    )
  } catch (error: any) {
    errorMessage.value = error.message || 'Error starting resume generation.'
    isLoading.value = false
  }
}

watch(() => resumeStore.status?.status, (newStatus) => {
    if (newStatus === 'completed' || newStatus === 'failed') {
    isLoading.value = false
    if (newStatus === 'completed' && resumeStore.result) {
      generatedResume.value = resumeStore.result.content
      agentOutputs.value = resumeStore.result.agent_outputs || ''
      resumeStore.companyName = resumeStore.result.company_name || ''
      resumeStore.jobTitle = resumeStore.result.job_title || ''
    } else if (newStatus === 'failed') {
      errorMessage.value = resumeStore.error || 'Resume generation failed'
    }
  }
})

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

/* Ensure drag-drop component matches textarea height exactly */
.drag-drop-fixed-height {
  height: 380px !important;
}

/* Override the DragDropFileUpload component's min-height */
.drag-drop-fixed-height :deep(.drag-drop-zone) {
  height: 100% !important;
  min-height: unset !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
}
</style>
