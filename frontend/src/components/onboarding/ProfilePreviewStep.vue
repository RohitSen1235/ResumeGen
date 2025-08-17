<template>
  <div class="text-center">
    <!-- Step Title -->
    <div class="text-h5 font-weight-bold mb-2 text-grey-darken-3">
      <v-icon icon="mdi-account-check-outline" class="mr-2" color="primary"></v-icon>
      Profile Preview
    </div>
    
    <!-- Step Description -->
    <div class="text-body-1 text-grey-darken-1 mb-6">
      Review your profile information before completing the setup
    </div>

    <!-- Profile Summary Card -->
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4 text-left">
        <v-icon icon="mdi-account-circle-outline" class="mr-2" color="primary"></v-icon>
        Your Profile Summary
      </div>

      <v-row>
        <!-- Basic Information -->
        <v-col cols="12" md="6">
          <v-card variant="tonal" color="blue-lighten-5" class="pa-4 h-100">
            <div class="text-subtitle-1 font-weight-bold mb-3 text-blue-darken-2">
              <v-icon icon="mdi-information-outline" class="mr-1"></v-icon>
              Basic Information
            </div>
            
            <div v-if="onboarding.data.fullName" class="text-body-2 mb-2">
              <span class="font-weight-medium">Name:</span> {{ onboarding.data.fullName }}
            </div>
            
            <div class="text-body-2 mb-2">
              <span class="font-weight-medium">Email:</span> {{ auth.user?.email }}
            </div>
            
            <div v-if="onboarding.data.linkedinUrl" class="text-body-2 mb-2">
              <span class="font-weight-medium">LinkedIn:</span>
              <a :href="onboarding.data.linkedinUrl" target="_blank" class="text-primary ml-1">
                {{ formatLinkedInUrl(onboarding.data.linkedinUrl) }}
                <v-icon icon="mdi-open-in-new" size="small" class="ml-1"></v-icon>
              </a>
            </div>
            
            <div v-if="onboarding.data.portfolioUrl" class="text-body-2 mb-2">
              <span class="font-weight-medium">Portfolio:</span>
              <a :href="onboarding.data.portfolioUrl" target="_blank" class="text-primary ml-1">
                {{ formatPortfolioUrl(onboarding.data.portfolioUrl) }}
                <v-icon icon="mdi-open-in-new" size="small" class="ml-1"></v-icon>
              </a>
            </div>

            <div v-if="!onboarding.data.linkedinUrl && !onboarding.data.portfolioUrl" class="text-body-2 text-grey-darken-1">
              No additional links provided
            </div>
          </v-card>
        </v-col>

        <!-- Resume Information -->
        <v-col cols="12" md="6">
          <v-card variant="tonal" color="green-lighten-5" class="pa-4 h-100">
            <div class="text-subtitle-1 font-weight-bold mb-3 text-green-darken-2">
              <v-icon icon="mdi-file-document-outline" class="mr-1"></v-icon>
              Resume Information
            </div>
            
            <div v-if="onboarding.data.hasResume && onboarding.data.resumePath" class="mb-3">
              <div class="text-body-2 mb-2">
                <span class="font-weight-medium">Resume uploaded:</span>
                <v-icon icon="mdi-check-circle" color="success" size="small" class="ml-1"></v-icon>
              </div>
              
              <div class="text-body-2 mb-2">
                <span class="font-weight-medium">AI Extraction:</span>
                {{ onboarding.data.useResumeSections ? 'Enabled' : 'Disabled' }}
              </div>

              <div v-if="extractedSectionsCount > 0" class="text-body-2">
                <span class="font-weight-medium">Sections found:</span> {{ extractedSectionsCount }}
              </div>
            </div>
            
            <div v-else class="text-body-2 text-grey-darken-1">
              No resume uploaded - profile will be built manually
            </div>
          </v-card>
        </v-col>
      </v-row>
    </v-card>

    <!-- Extracted Data Preview (if available) -->
    <v-expand-transition>
      <v-card
        v-if="onboarding.data.parsedResumeData && extractedSectionsCount > 0"
        variant="outlined"
        class="pa-6 mb-6"
        rounded="lg"
      >
        <div class="text-h6 mb-4 text-left">
          <v-icon icon="mdi-brain" class="mr-2" color="primary"></v-icon>
          AI Extracted Information
        </div>

        <v-row>
          <v-col cols="12" md="6" v-if="extractedSections.skills.length">
            <div class="text-subtitle-2 font-weight-bold mb-2">Skills ({{ extractedSections.skills.length }})</div>
            <v-chip-group>
              <v-chip
                v-for="skill in extractedSections.skills.slice(0, 8)"
                :key="skill"
                size="small"
                variant="outlined"
                color="primary"
              >
                {{ skill }}
              </v-chip>
              <v-chip
                v-if="extractedSections.skills.length > 8"
                size="small"
                variant="text"
              >
                +{{ extractedSections.skills.length - 8 }} more
              </v-chip>
            </v-chip-group>
          </v-col>
          
          <v-col cols="12" md="6" v-if="extractedSections.experience.length">
            <div class="text-subtitle-2 font-weight-bold mb-2">Work Experience</div>
            <div class="text-body-2 mb-2">
              {{ extractedSections.experience.length }} position{{ extractedSections.experience.length > 1 ? 's' : '' }} found
            </div>
            <div v-for="(exp, index) in extractedSections.experience.slice(0, 2)" :key="index" class="text-caption text-grey-darken-1 mb-1">
              • {{ exp.substring(0, 60) }}{{ exp.length > 60 ? '...' : '' }}
            </div>
            <div v-if="extractedSections.experience.length > 2" class="text-caption text-grey-darken-1">
              +{{ extractedSections.experience.length - 2 }} more experiences
            </div>
          </v-col>
          
          <v-col cols="12" md="6" v-if="extractedSections.education.length">
            <div class="text-subtitle-2 font-weight-bold mb-2">Education</div>
            <div class="text-body-2 mb-2">
              {{ extractedSections.education.length }} record{{ extractedSections.education.length > 1 ? 's' : '' }} found
            </div>
            <div v-for="(edu, index) in extractedSections.education.slice(0, 2)" :key="index" class="text-caption text-grey-darken-1 mb-1">
              • {{ edu.substring(0, 60) }}{{ edu.length > 60 ? '...' : '' }}
            </div>
          </v-col>
          
          <v-col cols="12" md="6" v-if="extractedSections.projects.length">
            <div class="text-subtitle-2 font-weight-bold mb-2">Projects</div>
            <div class="text-body-2 mb-2">
              {{ extractedSections.projects.length }} project{{ extractedSections.projects.length > 1 ? 's' : '' }} found
            </div>
            <div v-for="(project, index) in extractedSections.projects.slice(0, 2)" :key="index" class="text-caption text-grey-darken-1 mb-1">
              • {{ project.substring(0, 60) }}{{ project.length > 60 ? '...' : '' }}
            </div>
          </v-col>
        </v-row>
      </v-card>
    </v-expand-transition>

    <!-- Next Steps Information -->
    <v-card variant="tonal" color="orange-lighten-5" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-3 text-orange-darken-2">
        <v-icon icon="mdi-rocket-launch-outline" class="mr-2"></v-icon>
        What happens next?
      </div>
      
      <v-row>
        <v-col cols="12" md="4">
          <div class="text-center">
            <v-icon icon="mdi-account-cog" size="48" color="orange-darken-1" class="mb-2"></v-icon>
            <div class="text-subtitle-2 font-weight-bold mb-1">Profile Creation</div>
            <div class="text-body-2 text-grey-darken-1">
              Your profile will be created with the information provided
            </div>
          </div>
        </v-col>
        
        <v-col cols="12" md="4" v-if="onboarding.data.parsedResumeData">
          <div class="text-center">
            <v-icon icon="mdi-database-import" size="48" color="orange-darken-1" class="mb-2"></v-icon>
            <div class="text-subtitle-2 font-weight-bold mb-1">Data Import</div>
            <div class="text-body-2 text-grey-darken-1">
              AI-extracted sections will be imported to your profile
            </div>
          </div>
        </v-col>
        
        <v-col cols="12" :md="onboarding.data.parsedResumeData ? 4 : 8">
          <div class="text-center">
            <v-icon icon="mdi-file-document-edit" size="48" color="orange-darken-1" class="mb-2"></v-icon>
            <div class="text-subtitle-2 font-weight-bold mb-1">Resume Building</div>
            <div class="text-body-2 text-grey-darken-1">
              You'll be redirected to start building your optimized resume
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card>

    <!-- Final Confirmation -->
    <v-alert type="info" variant="tonal" class="mb-6">
      <div class="text-body-1">
        <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
        <strong>Good to know:</strong> You can always edit and update your profile information later from your dashboard.
      </div>
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useOnboardingStore } from '@/store/onboarding'
import { useAuthStore } from '@/store/auth'

const onboarding = useOnboardingStore()
const auth = useAuthStore()

// Computed
const extractedSectionsCount = computed(() => {
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

// Helper functions
const formatLinkedInUrl = (url: string) => {
  try {
    const urlObj = new URL(url)
    return urlObj.pathname.replace('/in/', '').replace('/', '')
  } catch {
    return url
  }
}

const formatPortfolioUrl = (url: string) => {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname + (urlObj.pathname !== '/' ? urlObj.pathname : '')
  } catch {
    return url
  }
}
</script>

<style scoped>
.v-card.h-100 {
  height: 100%;
}
</style>
