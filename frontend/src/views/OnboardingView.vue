<template>
  <v-container fluid class="fill-height pa-0" style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" md="10" lg="8">
        <v-card class="elevation-12 rounded-xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.9);">
          <!-- Header -->
          <v-card-title class="text-center pa-6">
            <div class="text-h4 font-weight-bold text-grey-darken-3 mb-2">
              Welcome to Resume Genie!
            </div>
            <div class="text-body-1 text-grey-darken-1">
              Let's set up your profile in just a few steps
            </div>
          </v-card-title>

          <!-- Progress Tracker -->
          <div class="px-6 pb-4">
            <v-progress-linear
              :model-value="onboarding.progress"
              color="primary"
              height="8"
              rounded
              class="mb-4"
            ></v-progress-linear>
            
            <div class="d-flex justify-space-between text-caption text-grey-darken-1">
              <span :class="{ 'text-primary font-weight-bold': onboarding.currentStep >= 1 }">
                Name
              </span>
              <span :class="{ 'text-primary font-weight-bold': onboarding.currentStep >= 2 }">
                Resume
              </span>
              <span :class="{ 'text-primary font-weight-bold': onboarding.currentStep >= 3 }">
                LinkedIn
              </span>
              <span :class="{ 'text-primary font-weight-bold': onboarding.currentStep >= 4 }">
                Portfolio
              </span>
              <span :class="{ 'text-primary font-weight-bold': onboarding.currentStep >= 5 }">
                Preview
              </span>
            </div>
          </div>

    <!-- Step Content -->
    <v-card-text class="pa-8">
      <!-- Step 1: Name Collection -->
      <NameStep 
        v-if="onboarding.currentStep === 1"
        :source="source"
      />
      
      <!-- Step 2: Resume Upload -->
      <ResumeUploadStep 
        v-if="onboarding.currentStep === 2"
        :source="source"
      />
      
      <!-- Step 3: LinkedIn Profile -->
      <LinkedinStep 
        v-if="onboarding.currentStep === 3"
        :source="source"
      />
      
      <!-- Step 4: Portfolio Website -->
      <PortfolioStep 
        v-if="onboarding.currentStep === 4"
        :source="source"
      />
      
      <!-- Step 5: Profile Preview -->
      <ProfilePreviewStep 
        v-if="onboarding.currentStep === 5"
        :source="source"
      />
    </v-card-text>

          <!-- Navigation -->
          <v-card-actions class="pa-6 pt-0">
            <v-btn
              v-if="onboarding.currentStep > 1"
              variant="outlined"
              color="grey"
              @click="onboarding.prevStep"
              :disabled="onboarding.loading"
            >
              <v-icon icon="mdi-chevron-left" class="mr-1"></v-icon>
              Back
            </v-btn>

            <v-spacer></v-spacer>

            <v-btn
              v-if="onboarding.currentStep < onboarding.totalSteps"
              color="primary"
              @click="onboarding.nextStep"
              :disabled="!onboarding.canProceed || onboarding.loading"
              :loading="onboarding.loading"
            >
              Next
              <v-icon icon="mdi-chevron-right" class="ml-1"></v-icon>
            </v-btn>

            <v-btn
              v-else
              color="success"
              size="large"
              @click="completeOnboarding"
              :disabled="onboarding.loading"
              :loading="onboarding.loading"
            >
              Complete Setup
              <v-icon icon="mdi-check" class="ml-1"></v-icon>
            </v-btn>
          </v-card-actions>

          <!-- Error Alert -->
          <v-alert
            v-if="onboarding.error"
            type="error"
            variant="tonal"
            class="ma-6 mt-0"
            closable
            @click:close="onboarding.error = ''"
          >
            {{ onboarding.error }}
          </v-alert>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useOnboardingStore } from '@/store/onboarding'
import { useAuthStore } from '@/store/auth'
import NameStep from '@/components/onboarding/NameStep.vue'
import ResumeUploadStep from '@/components/onboarding/ResumeUploadStep.vue'
import LinkedinStep from '@/components/onboarding/LinkedinStep.vue'
import PortfolioStep from '@/components/onboarding/PortfolioStep.vue'
import ProfilePreviewStep from '@/components/onboarding/ProfilePreviewStep.vue'

const router = useRouter()
const route = useRoute()
const onboarding = useOnboardingStore()
const auth = useAuthStore()

// Computed source from onboarding data
const source = computed(() => onboarding.data.source)

onMounted(async () => {
  // Check if user is authenticated
  if (!auth.isAuthenticated) {
    router.push('/login')
    return
  }

  // Fetch latest user data to check onboarding status
  try {
    await auth.fetchUser()
    
    // If user has already completed onboarding, redirect to resume builder
    if (auth.hasCompletedOnboarding) {
      router.push('/resume-builder')
      return
    }
  } catch (error) {
    console.error('Failed to fetch user data:', error)
  }

  // Initialize onboarding based on source
  const source = route.query.source as string
  if (source === 'linkedin') {
    onboarding.updateData({ 
      source: 'linkedin',
      linkedinUrl: auth.user?.profile?.linkedin_url || ''
    })
  } else {
    onboarding.updateData({ source: 'standard' })
  }

  // Reset onboarding state
  onboarding.reset()
})

const completeOnboarding = async () => {
  try {
    console.log('Starting onboarding completion...')
    await onboarding.completeOnboarding()
    console.log('Onboarding completed successfully')
    
    // Refresh user data to ensure we have the latest state
    await auth.fetchUser()
    
    // Always redirect to resume builder after successful onboarding
    router.push('/resume-builder')
  } catch (error) {
    console.error('Onboarding completion failed:', error)
    // Error is already set in the store, so it will be displayed
  }
}
</script>

<style scoped>
.v-progress-linear {
  border-radius: 4px;
}
</style>
