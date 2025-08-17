<template>
  <div class="text-center">
    <!-- Step Title -->
    <div class="text-h5 font-weight-bold mb-2 text-grey-darken-3">
      <v-icon icon="mdi-file-document-outline" class="mr-2" color="primary"></v-icon>
      {{ stepTitle }}
    </div>
    
    <!-- Step Description -->
    <div class="text-body-1 text-grey-darken-1 mb-6">
      {{ stepDescription }}
    </div>

    <!-- Resume Question -->
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4">Do you already have a resume?</div>
      
      <v-btn-toggle
        v-model="hasResumeSelection"
        color="primary"
        variant="outlined"
        divided
        mandatory
        class="mb-4"
      >
        <v-btn value="yes" size="large" class="px-8">
          <v-icon icon="mdi-check-circle-outline" class="mr-2"></v-icon>
          Yes, I have one
        </v-btn>
        <v-btn value="no" size="large" class="px-8">
          <v-icon icon="mdi-close-circle-outline" class="mr-2"></v-icon>
          No, I don't
        </v-btn>
      </v-btn-toggle>

      <!-- Resume Upload Section -->
      <v-expand-transition>
        <div v-if="hasResumeSelection === 'yes'" class="mt-6">
          <v-divider class="mb-6"></v-divider>
          
          <div class="text-body-1 text-grey-darken-1 mb-4">
            Upload your resume and our AI will automatically extract your profile information
          </div>

          <drag-drop-file-upload
            v-model="resumeFile"
            accept=".pdf"
            :max-size="10"
            :error-message="uploadError"
            @file-selected="handleResumeUpload"
            title="Upload your Resume / CV"
            supported-formats="PDF"
            :loading="onboarding.loading"
            :show-loading-overlay="true"
            class="mb-4"
          />

          <!-- Upload Success -->
        <v-alert
          v-if="uploadSuccess"
          type="success"
          variant="tonal"
          class="mb-4"
        >
          <div>
            <div class="font-weight-bold">Resume uploaded successfully!</div>
          </div>
        </v-alert>

          <!-- Parsed Data Preview -->
          <v-expand-transition>
            <v-card
              v-if="onboarding.data.parsedResumeData"
              variant="outlined"
              class="mt-4"
              rounded="lg"
            >
              <v-card-title class="text-h6 pb-2">
                <v-icon icon="mdi-brain" class="mr-2" color="primary"></v-icon>
                Extracted Information Preview
              </v-card-title>
              <v-card-text>
                <div class="text-body-2 text-grey-darken-1 mb-3">
                  Preview of information extracted from your resume:
                </div>
                
                <v-row>
                  <v-col cols="12" md="6" v-if="extractedSections.skills.length">
                    <div class="text-subtitle-2 font-weight-bold mb-2">Skills</div>
                    <v-chip-group>
                      <v-chip
                        v-for="skill in extractedSections.skills.slice(0, 5)"
                        :key="skill.name || skill"
                        size="small"
                        variant="outlined"
                      >
                        {{ skill.name || skill }}
                      </v-chip>
                      <v-chip
                        v-if="extractedSections.skills.length > 5"
                        size="small"
                        variant="text"
                      >
                        +{{ extractedSections.skills.length - 5 }} more
                      </v-chip>
                    </v-chip-group>
                  </v-col>
                  
                  <v-col cols="12" md="6" v-if="extractedSections.experience.length">
                    <div class="text-subtitle-2 font-weight-bold mb-2">Experience</div>
                    <div class="text-body-2">
                      {{ extractedSections.experience.length }} work experience{{ extractedSections.experience.length > 1 ? 's' : '' }} found
                    </div>
                  </v-col>
                  
                  <v-col cols="12" md="6" v-if="extractedSections.education.length">
                    <div class="text-subtitle-2 font-weight-bold mb-2">Education</div>
                    <div class="text-body-2">
                      {{ extractedSections.education.length }} education record{{ extractedSections.education.length > 1 ? 's' : '' }} found
                    </div>
                  </v-col>
                  
                  <v-col cols="12" md="6" v-if="extractedSections.projects.length">
                    <div class="text-subtitle-2 font-weight-bold mb-2">Projects</div>
                    <div class="text-body-2">
                      {{ extractedSections.projects.length }} project{{ extractedSections.projects.length > 1 ? 's' : '' }} found
                    </div>
                  </v-col>
                </v-row>

                <v-alert
                  type="info"
                  variant="tonal"
                  class="mt-4"
                  density="compact"
                >
                  <div class="text-body-2">
                    This information will be used to populate your profile sections. You can edit and refine it later.
                  </div>
                </v-alert>
              </v-card-text>
            </v-card>
          </v-expand-transition>
        </div>
      </v-expand-transition>

      <!-- No Resume Selected -->
      <v-expand-transition>
        <div v-if="hasResumeSelection === 'no'" class="mt-6">
          <v-divider class="mb-6"></v-divider>
          
          <v-alert type="info" variant="tonal">
            <div class="d-flex align-center">
              <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
              <div>
                <div class="font-weight-bold">No problem!</div>
                <div class="text-body-2">
                  We'll help you build your profile from scratch in the next steps.
                </div>
              </div>
            </div>
          </v-alert>
        </div>
      </v-expand-transition>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useOnboardingStore } from '@/store/onboarding'
import DragDropFileUpload from '@/components/DragDropFileUpload.vue'

interface Props {
  source: 'standard' | 'linkedin'
}

const props = defineProps<Props>()
const onboarding = useOnboardingStore()

// Local state
const resumeFile = ref<File | null>(null)
const uploadError = ref('')
const uploadSuccess = ref(false)
const hasResumeSelection = ref<'yes' | 'no' | null>(null)

// Computed
const stepTitle = computed(() => {
  return props.source === 'linkedin' 
    ? 'Hello! Do you already have a resume?' 
    : 'Let\'s start with your resume'
})

const stepDescription = computed(() => {
  return props.source === 'linkedin'
    ? 'We\'ve got your LinkedIn profile, but a resume can help us build a more complete picture.'
    : 'If you have an existing resume, we can use AI to automatically populate your profile sections.'
})

const parsedSectionsCount = computed(() => {
  if (!onboarding.data.parsedResumeData) return 0
  
  const data = onboarding.data.parsedResumeData
  let count = 0
  
  if (data.skills?.length) count++
  if (data.past_experiences?.length) count++
  if (data.education?.length) count++
  if (data.Projects?.length) count++
  if (data.professional_summary) count++
  
  return count
})

const extractedSections = computed(() => {
  const data = onboarding.data.parsedResumeData
  if (!data) return { skills: [], experience: [], education: [], projects: [] }
  
  return {
    skills: data.skills || [],
    experience: data.past_experiences || [],
    education: data.education || [],
    projects: data.Projects || []
  }
})

// Watch for selection changes
watch(hasResumeSelection, (newValue) => {
  if (newValue === 'yes') {
    onboarding.updateData({ hasResume: true })
  } else if (newValue === 'no') {
    onboarding.updateData({ 
      hasResume: false,
      useResumeSections: false,
      resumeFile: null,
      resumePath: null,
      parsedResumeData: null
    })
    uploadSuccess.value = false
    resumeFile.value = null
  }
})

// Initialize from store if data exists
if (onboarding.data.hasResume !== null) {
  hasResumeSelection.value = onboarding.data.hasResume ? 'yes' : 'no'
}

if (onboarding.data.resumeFile) {
  resumeFile.value = onboarding.data.resumeFile
  uploadSuccess.value = true
}

const handleResumeUpload = async () => {
  if (!resumeFile.value) return

  try {
    uploadError.value = ''
    uploadSuccess.value = false
    
    await onboarding.uploadResume(resumeFile.value)
    uploadSuccess.value = true
  } catch (error: any) {
    uploadError.value = error.message || 'Failed to upload resume'
    uploadSuccess.value = false
  }
}
</script>

<style scoped>
.v-btn-toggle {
  width: 100%;
}

.v-btn-toggle .v-btn {
  flex: 1;
}
</style>
