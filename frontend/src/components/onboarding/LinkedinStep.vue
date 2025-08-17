<template>
  <div class="text-center">
    <!-- Step Title -->
    <div class="text-h5 font-weight-bold mb-2 text-grey-darken-3">
      <v-icon icon="mdi-linkedin" class="mr-2" color="primary"></v-icon>
      {{ stepTitle }}
    </div>
    
    <!-- Step Description -->
    <div class="text-body-1 text-grey-darken-1 mb-6">
      {{ stepDescription }}
    </div>

    <!-- LinkedIn Profile Section -->
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4">{{ questionText }}</div>
      
      <!-- For LinkedIn users - show confirmation -->
      <div v-if="source === 'linkedin'" class="mb-4">
        <v-alert type="info" variant="tonal" class="mb-4">
          <div class="d-flex align-center">
            <v-icon icon="mdi-linkedin" class="mr-2"></v-icon>
            <div>
              <div class="font-weight-bold">LinkedIn Profile Detected</div>
              <div class="text-body-2">
                We've automatically detected your LinkedIn profile from your sign-in.
              </div>
            </div>
          </div>
        </v-alert>
      </div>

      <!-- LinkedIn URL Input -->
      <v-text-field
        v-model="linkedinUrl"
        label="LinkedIn Profile URL"
        variant="outlined"
        density="comfortable"
        prepend-inner-icon="mdi-linkedin"
        placeholder="https://www.linkedin.com/in/your-profile"
        :rules="linkedinRules"
        class="mb-4"
        :readonly="source === 'linkedin' && !!initialLinkedinUrl"
      >
        <template v-slot:append-inner>
          <v-tooltip text="Copy your LinkedIn profile URL from your browser">
            <template v-slot:activator="{ props }">
              <v-icon
                v-bind="props"
                icon="mdi-help-circle-outline"
                color="grey-darken-1"
              ></v-icon>
            </template>
          </v-tooltip>
        </template>
      </v-text-field>

      <!-- Instructions -->
      <v-expansion-panels variant="accordion" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <v-icon icon="mdi-help-circle-outline" class="mr-2"></v-icon>
            How to get your LinkedIn profile URL
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <div class="text-body-2">
              <ol class="pl-4">
                <li class="mb-2">Go to <a href="https://linkedin.com" target="_blank" class="text-primary">linkedin.com</a> and sign in</li>
                <li class="mb-2">Click on your profile picture or "Me" in the top navigation</li>
                <li class="mb-2">Select "View profile" from the dropdown</li>
                <li class="mb-2">Copy the URL from your browser's address bar</li>
                <li>It should look like: https://www.linkedin.com/in/your-name</li>
              </ol>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Why we need this -->
      <v-card variant="tonal" color="blue-lighten-5" class="pa-4 mb-4">
        <div class="text-subtitle-2 font-weight-bold mb-2 text-blue-darken-2">
          <v-icon icon="mdi-information-outline" class="mr-1"></v-icon>
          Why do we need your LinkedIn profile?
        </div>
        <div class="text-body-2 text-blue-darken-1">
          <ul class="pl-4">
            <li>Include it in your generated resumes for easy contact</li>
            <li>Help recruiters find and connect with you</li>
            <li>Showcase your professional network and endorsements</li>
            <li>Maintain consistency across your professional presence</li>
          </ul>
        </div>
      </v-card>

      <!-- Skip Option -->
      <div class="text-center">
        <v-btn
          variant="text"
          color="grey-darken-1"
          @click="skipLinkedIn"
          :disabled="onboarding.loading"
        >
          Skip this step
        </v-btn>
      </div>
    </v-card>

    <!-- Validation Success -->
    <v-alert
      v-if="validationSuccess"
      type="success"
      variant="tonal"
      class="mb-4"
    >
      <div class="d-flex align-center">
        <v-icon icon="mdi-check-circle" class="mr-2"></v-icon>
        <div>
          <div class="font-weight-bold">LinkedIn profile validated!</div>
          <div class="text-body-2">
            Your LinkedIn profile URL looks good and will be included in your resume.
          </div>
        </div>
      </div>
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useOnboardingStore } from '@/store/onboarding'

interface Props {
  source: 'standard' | 'linkedin'
}

const props = defineProps<Props>()
const onboarding = useOnboardingStore()

// Local state
const linkedinUrl = ref('')
const validationSuccess = ref(false)
const initialLinkedinUrl = ref('')

// Computed
const stepTitle = computed(() => {
  return props.source === 'linkedin' 
    ? 'Is this your LinkedIn Profile URL?' 
    : 'LinkedIn Profile URL'
})

const stepDescription = computed(() => {
  return props.source === 'linkedin'
    ? 'We can include your LinkedIn profile in your resume for better networking opportunities.'
    : 'Adding your LinkedIn profile helps recruiters connect with you and validates your professional presence.'
})

const questionText = computed(() => {
  return props.source === 'linkedin'
    ? 'Please confirm or update your LinkedIn profile URL:'
    : 'Do you have a LinkedIn profile? (Optional)'
})

// Validation rules
const linkedinRules = [
  (v: string) => {
    if (!v) return true // Optional field
    const linkedinPattern = /^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?$/
    return linkedinPattern.test(v) || 'Please enter a valid LinkedIn profile URL (e.g., https://www.linkedin.com/in/your-name)'
  }
]

// Watch for URL changes
watch(linkedinUrl, (newValue) => {
  onboarding.updateData({ linkedinUrl: newValue })
  
  // Validate URL
  if (newValue && linkedinRules[0](newValue) === true) {
    validationSuccess.value = true
  } else {
    validationSuccess.value = false
  }
})

// Initialize from store
onMounted(() => {
  if (onboarding.data.linkedinUrl) {
    linkedinUrl.value = onboarding.data.linkedinUrl
    initialLinkedinUrl.value = onboarding.data.linkedinUrl
  }
})

const skipLinkedIn = () => {
  linkedinUrl.value = ''
  onboarding.updateData({ linkedinUrl: '' })
  validationSuccess.value = false
}
</script>

<style scoped>
.v-expansion-panels {
  box-shadow: none;
}

.v-expansion-panel {
  border: 1px solid rgba(0, 0, 0, 0.12);
  border-radius: 8px;
}

ol li {
  margin-bottom: 8px;
}

ul li {
  margin-bottom: 4px;
}
</style>
