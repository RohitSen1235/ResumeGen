<template>
  <div class="text-center">
    <!-- Step Title -->
    <div class="text-h5 font-weight-bold mb-2 text-grey-darken-3">
      <v-icon icon="mdi-account-outline" class="mr-2" color="primary"></v-icon>
      {{ stepTitle }}
    </div>
    
    <!-- Step Description -->
    <div class="text-body-1 text-grey-darken-1 mb-6">
      {{ stepDescription }}
    </div>

    <!-- Name Input Section -->
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4">What's your full name?</div>
      
      <v-text-field
        v-model="fullName"
        label="Full Name"
        variant="outlined"
        density="comfortable"
        prepend-inner-icon="mdi-account-outline"
        placeholder="Enter your full name"
        :rules="nameRules"
        class="mb-4"
        autofocus
      >
        <template v-slot:append-inner>
          <v-tooltip text="Enter your full name as you'd like it to appear on your resume">
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

      <!-- Name Preview -->
      <v-expand-transition>
        <v-card
          v-if="fullName.trim().length > 0"
          variant="tonal"
          color="green-lighten-5"
          class="pa-4"
          rounded="lg"
        >
          <div class="text-subtitle-2 font-weight-bold mb-2 text-green-darken-2">
            <v-icon icon="mdi-eye-outline" class="mr-1"></v-icon>
            Preview
          </div>
          <div class="text-body-1 text-green-darken-1">
            Your name will appear as: <strong>{{ fullName.trim() }}</strong>
          </div>
        </v-card>
      </v-expand-transition>

      <!-- Why we need this -->
      <v-card variant="tonal" color="blue-lighten-5" class="pa-4 mt-4">
        <div class="text-subtitle-2 font-weight-bold mb-2 text-blue-darken-2">
          <v-icon icon="mdi-information-outline" class="mr-1"></v-icon>
          Why do we need your name?
        </div>
        <div class="text-body-2 text-blue-darken-1">
          <ul class="pl-4">
            <li>Display prominently on your generated resumes</li>
            <li>Personalize your profile and dashboard experience</li>
            <li>Help recruiters identify you professionally</li>
            <li>Ensure consistency across all your documents</li>
          </ul>
        </div>
      </v-card>
    </v-card>

    <!-- Validation Success -->
    <v-alert
      v-if="validationSuccess"
      type="success"
      variant="tonal"
      class="mb-4"
    >
      <div>
        <div class="font-weight-bold">Perfect!</div>
        <div class="text-body-2">
          Your name looks good and will be used throughout your profile.
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
const fullName = ref('')
const validationSuccess = ref(false)

// Computed
const stepTitle = computed(() => {
  return props.source === 'linkedin' 
    ? 'Welcome! Let\'s get your name' 
    : 'Let\'s start with your name'
})

const stepDescription = computed(() => {
  return props.source === 'linkedin'
    ? 'We\'ll use your name to personalize your resume and profile.'
    : 'Your name will be prominently displayed on all your generated resumes.'
})

// Validation rules
const nameRules = [
  (v: string) => !!v?.trim() || 'Name is required',
  (v: string) => (v?.trim().length >= 2) || 'Name must be at least 2 characters',
  (v: string) => (v?.trim().length <= 100) || 'Name must be less than 100 characters',
  (v: string) => /^[a-zA-Z\s\-'\.]+$/.test(v?.trim()) || 'Name can only contain letters, spaces, hyphens, apostrophes, and periods'
]

// Watch for name changes
watch(fullName, (newValue) => {
  const trimmedValue = newValue.trim()
  onboarding.updateData({ fullName: trimmedValue })
  
  // Validate name
  if (trimmedValue && nameRules.every(rule => rule(trimmedValue) === true)) {
    validationSuccess.value = true
  } else {
    validationSuccess.value = false
  }
})

// Initialize from store
onMounted(() => {
  if (onboarding.data.fullName) {
    fullName.value = onboarding.data.fullName
  }
})
</script>

<style scoped>
ul li {
  margin-bottom: 4px;
}
</style>
