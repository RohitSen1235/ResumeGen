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

    <!-- Basic Profile Information -->
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4 text-left">
        <v-icon icon="mdi-account-circle-outline" class="mr-2" color="primary"></v-icon>
        Basic Information
      </div>

      <v-row>
        <v-col cols="12" md="6">
          <v-list density="compact">
            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-account" color="primary"></v-icon>
              </template>
              <v-list-item-title class="font-weight-medium">Full Name</v-list-item-title>
              <v-list-item-subtitle>{{ onboarding.data.fullName || 'Not provided' }}</v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-email" color="primary"></v-icon>
              </template>
              <v-list-item-title class="font-weight-medium">Email</v-list-item-title>
              <v-list-item-subtitle>{{ auth.user?.email }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-map-marker" color="primary"></v-icon>
              </template>
              <v-list-item-title class="font-weight-medium">Location</v-list-item-title>
              <v-list-item-subtitle>{{ [onboarding.data.city, onboarding.data.country].filter(Boolean).join(', ') || 'Not provided' }}</v-list-item-subtitle>
            </v-list-item>
            <v-list-item>
              <template v-slot:prepend>
                <v-icon icon="mdi-factory" color="primary"></v-icon>
              </template>
              <v-list-item-title class="font-weight-medium">Industry</v-list-item-title>
              <v-list-item-subtitle>{{ onboarding.data.industry || 'Not provided' }}</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-col>
        
        <v-col cols="12" md="6">
          <v-list density="compact">
            <v-list-item v-if="onboarding.data.linkedinUrl">
              <template v-slot:prepend>
                <v-icon icon="mdi-linkedin" color="primary"></v-icon>
              </template>
              <v-list-item-title class="font-weight-medium">LinkedIn</v-list-item-title>
              <v-list-item-subtitle>
                <a :href="onboarding.data.linkedinUrl" target="_blank" class="text-primary text-decoration-none">
                  {{ formatLinkedInUrl(onboarding.data.linkedinUrl) }}
                  <v-icon icon="mdi-open-in-new" size="small" class="ml-1"></v-icon>
                </a>
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item v-if="onboarding.data.portfolioUrl">
              <template v-slot:prepend>
                <v-icon icon="mdi-web" color="primary"></v-icon>
              </template>
              <v-list-item-title class="font-weight-medium">Portfolio</v-list-item-title>
              <v-list-item-subtitle>
                <a :href="onboarding.data.portfolioUrl" target="_blank" class="text-primary text-decoration-none">
                  {{ formatPortfolioUrl(onboarding.data.portfolioUrl) }}
                  <v-icon icon="mdi-open-in-new" size="small" class="ml-1"></v-icon>
                </a>
              </v-list-item-subtitle>
            </v-list-item>
            
            <v-list-item v-if="!onboarding.data.linkedinUrl && !onboarding.data.portfolioUrl">
              <template v-slot:prepend>
                <v-icon icon="mdi-information-outline" color="grey"></v-icon>
              </template>
              <v-list-item-title class="text-grey-darken-1">No additional links provided</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-col>
      </v-row>
    </v-card>

    <!-- Resume Information -->
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4 text-left">
        <v-icon icon="mdi-file-document-outline" class="mr-2" color="primary"></v-icon>
        Resume Information
      </div>
      
      <div v-if="onboarding.data.hasResume && onboarding.data.resumePath">
        <v-alert type="success" variant="tonal" class="mb-4">
          <div>
            <div class="font-weight-bold">Resume uploaded successfully!</div>
            <div class="text-body-2">
              AI extraction {{ onboarding.data.useResumeSections ? 'enabled' : 'disabled' }}
              <span v-if="extractedSectionsCount > 0"> - {{ extractedSectionsCount }} sections found</span>
            </div>
            <div v-if="extractedSectionTitles.length > 0" class="mt-2">
              <span class="font-weight-medium">Extracted Sections:</span>
              <v-chip
                v-for="title in extractedSectionTitles"
                :key="title"
                size="small"
                class="ml-1"
                color="success"
                variant="outlined"
              >
                {{ title }}
              </v-chip>
            </div>
          </div>
        </v-alert>
      </div>
      
      <div v-else>
        <v-alert type="info" variant="tonal">
          <div class="d-flex align-center">
            <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
            <div>
              <div class="font-weight-bold">No resume uploaded</div>
              <div class="text-body-2">
                Your profile will be built manually using the information you provide
              </div>
            </div>
          </div>
        </v-alert>
      </div>
    </v-card>

    <!-- Extracted Data Preview (if available) -->
    <v-expand-transition>
      <div v-if="onboarding.data.parsedResumeData && extractedSectionsCount > 0">
        <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
          <div class="text-h6 mb-4 text-left">
            <v-icon icon="mdi-brain" class="mr-2" color="primary"></v-icon>
            Extracted Information from your Resume
            <v-chip size="small" color="success" class="ml-2">{{ extractedSectionsCount }} sections</v-chip>
          </div>

          <v-row>
            <!-- Skills Section -->
            <v-col cols="12" md="6" v-if="extractedSections.skills.length">
              <v-card variant="tonal" color="blue-lighten-5" class="pa-4 h-100">
                <div class="text-subtitle-1 font-weight-bold mb-3 text-blue-darken-2">
                  <v-icon icon="mdi-star-outline" class="mr-1"></v-icon>
                  Skills ({{ extractedSections.skills.length }})
                </div>
                
                <div class="d-flex flex-wrap ga-2">
                  <v-chip
                    v-for="skill in extractedSections.skills.slice(0, 12)"
                    :key="skill.name || skill"
                    size="small"
                    variant="outlined"
                    color="blue-darken-1"
                  >
                    {{ skill.name || skill }}
                  </v-chip>
                  <v-chip
                    v-if="extractedSections.skills.length > 12"
                    size="small"
                    variant="text"
                    color="blue-darken-1"
                  >
                    +{{ extractedSections.skills.length - 12 }} more
                  </v-chip>
                </div>
              </v-card>
            </v-col>
            
            <!-- Work Experience Section -->
            <v-col cols="12" md="6" v-if="extractedSections.experience.length">
              <v-card variant="tonal" color="green-lighten-5" class="pa-4 h-100">
                <div class="text-subtitle-1 font-weight-bold mb-3 text-green-darken-2">
                  <v-icon icon="mdi-briefcase-outline" class="mr-1"></v-icon>
                  Work Experience ({{ extractedSections.experience.length }})
                </div>
                
                <div v-for="(exp, index) in extractedSections.experience.slice(0, 3)" :key="index" class="mb-2">
                  <div class="text-body-2 font-weight-medium text-green-darken-2">
                    {{ exp.position || `Position ${index + 1}` }}
                  </div>
                  <div class="text-caption text-green-darken-1">
                    {{ exp.company || 'Company Name' }}
                  </div>
                  <div class="text-caption text-grey-darken-1 mt-1">
                    {{ (exp.description || exp).substring(0, 80) }}{{ (exp.description || exp).length > 80 ? '...' : '' }}
                  </div>
                </div>
                
                <div v-if="extractedSections.experience.length > 3" class="text-caption text-green-darken-1 mt-2">
                  +{{ extractedSections.experience.length - 3 }} more experiences
                </div>
              </v-card>
            </v-col>
            
            <!-- Education Section -->
            <v-col cols="12" md="6" v-if="extractedSections.education.length">
              <v-card variant="tonal" color="purple-lighten-5" class="pa-4 h-100">
                <div class="text-subtitle-1 font-weight-bold mb-3 text-purple-darken-2">
                  <v-icon icon="mdi-school-outline" class="mr-1"></v-icon>
                  Education ({{ extractedSections.education.length }})
                </div>
                
                <div v-for="(edu, index) in extractedSections.education.slice(0, 3)" :key="index" class="mb-2">
                  <div class="text-body-2 font-weight-medium text-purple-darken-2">
                    {{ edu.degree || edu }}
                  </div>
                  <div class="text-caption text-purple-darken-1">
                    {{ edu.institution || 'Institution' }}
                  </div>
                  <div v-if="edu.field_of_study" class="text-caption text-grey-darken-1">
                    {{ edu.field_of_study }}
                  </div>
                </div>
                
                <div v-if="extractedSections.education.length > 3" class="text-caption text-purple-darken-1 mt-2">
                  +{{ extractedSections.education.length - 3 }} more records
                </div>
              </v-card>
            </v-col>
            
            <!-- Projects Section -->
            <v-col cols="12" md="6" v-if="extractedSections.projects.length">
              <v-card variant="tonal" color="orange-lighten-5" class="pa-4 h-100">
                <div class="text-subtitle-1 font-weight-bold mb-3 text-orange-darken-2">
                  <v-icon icon="mdi-folder-outline" class="mr-1"></v-icon>
                  Projects ({{ extractedSections.projects.length }})
                </div>
                
                <div v-for="(project, index) in extractedSections.projects.slice(0, 3)" :key="index" class="mb-2">
                  <div class="text-body-2 font-weight-medium text-orange-darken-2">
                    {{ project.name || `Project ${index + 1}` }}
                  </div>
                  <div class="text-caption text-grey-darken-1 mt-1">
                    {{ (project.description || project).substring(0, 80) }}{{ (project.description || project).length > 80 ? '...' : '' }}
                  </div>
                </div>
                
                <div v-if="extractedSections.projects.length > 3" class="text-caption text-orange-darken-1 mt-2">
                  +{{ extractedSections.projects.length - 3 }} more projects
                </div>
              </v-card>
            </v-col>
          </v-row>

          <!-- Professional Summary -->
          <div v-if="onboarding.data.parsedResumeData.summary" class="mt-4">
            <v-card variant="tonal" color="indigo-lighten-5" class="pa-4">
              <div class="text-subtitle-1 font-weight-bold mb-3 text-indigo-darken-2">
                <v-icon icon="mdi-text-account" class="mr-1"></v-icon>
                Professional Summary
              </div>
              <div class="text-body-2 text-indigo-darken-1">
                {{ onboarding.data.parsedResumeData.summary }}
              </div>
            </v-card>
          </div>
        </v-card>
      </div>
    </v-expand-transition>

    <!-- Next Steps Information -->
    <v-card variant="tonal" color="success-lighten-5" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4 text-success-darken-2 text-center">
        <v-icon icon="mdi-rocket-launch-outline" class="mr-2"></v-icon>
        What happens next?
      </div>
      
      <v-row justify="center">
        <v-col cols="12" md="4">
          <div class="text-center">
            <v-avatar size="64" color="success-lighten-3" class="mb-3">
              <v-icon icon="mdi-account-cog" size="32" color="success-darken-1"></v-icon>
            </v-avatar>
            <div class="text-subtitle-2 font-weight-bold mb-2 text-success-darken-2">Profile Creation</div>
            <div class="text-body-2 text-grey-darken-1">
              Your profile will be created with all the information you've provided
            </div>
          </div>
        </v-col>
        
        <v-col cols="12" md="4" v-if="onboarding.data.parsedResumeData">
          <div class="text-center">
            <v-avatar size="64" color="success-lighten-3" class="mb-3">
              <v-icon icon="mdi-database-import" size="32" color="success-darken-1"></v-icon>
            </v-avatar>
            <div class="text-subtitle-2 font-weight-bold mb-2 text-success-darken-2">Data Import</div>
            <div class="text-body-2 text-grey-darken-1">
              AI-extracted sections will be imported and organized in your profile
            </div>
          </div>
        </v-col>
        
        <v-col cols="12" md="4">
          <div class="text-center">
            <v-avatar size="64" color="success-lighten-3" class="mb-3">
              <v-icon icon="mdi-file-document-edit" size="32" color="success-darken-1"></v-icon>
            </v-avatar>
            <div class="text-subtitle-2 font-weight-bold mb-2 text-success-darken-2">Resume Building</div>
            <div class="text-body-2 text-grey-darken-1">
              Start creating optimized resumes tailored to specific job opportunities
            </div>
          </div>
        </v-col>
      </v-row>
    </v-card>

    <!-- Final Confirmation -->
    <v-alert type="info" variant="tonal" class="mb-6">
      <div class="text-body-1">
        <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
        <strong>Good to know:</strong> You can always edit and update your profile information later from your dashboard. All extracted data can be refined and customized.
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
  if (data.work_experience?.length) count++
  if (data.education?.length) count++
  if (data.projects?.length) count++
  if (data.summary) count++
  
  return count
})

const extractedSections = computed(() => {
  const data = onboarding.data.parsedResumeData
  if (!data) return { skills: [], experience: [], education: [], projects: [] }
  
  return {
    skills: data.skills || [],
    experience: data.work_experience || [],
    education: data.education || [],
    projects: data.projects || []
  }
})

const extractedSectionTitles = computed(() => {
  if (!onboarding.data.parsedResumeData) return []
  
  const data = onboarding.data.parsedResumeData
  const titles = []
  
  if (data.summary) titles.push('Summary')
  if (data.work_experience?.length) titles.push('Work Experience')
  if (data.education?.length) titles.push('Education')
  if (data.skills?.length) titles.push('Skills')
  if (data.projects?.length) titles.push('Projects')
  
  return titles
})

// Helper functions
const formatLinkedInUrl = (url: string) => {
  try {
    const urlObj = new URL(url)
    return urlObj.pathname.replace('/in/', '').replace('/', '') || urlObj.hostname
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

.v-list-item {
  padding-left: 0;
  padding-right: 0;
}

.v-avatar {
  border: 2px solid rgba(var(--v-theme-success-lighten-2), 0.3);
}

.text-decoration-none {
  text-decoration: none !important;
}

.text-decoration-none:hover {
  text-decoration: underline !important;
}
</style>
