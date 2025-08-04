<template>
  <v-card class="progress-tracker" elevation="3" rounded="lg">
    <v-card-title class="d-flex align-center pa-4 bg-primary text-white rounded-t-lg">
      <v-icon icon="mdi-cog" class="mr-2 rotating" v-if="isGenerating"></v-icon>
      <v-icon icon="mdi-check-circle" class="mr-2" color="success" v-else-if="isCompleted"></v-icon>
      <v-icon icon="mdi-alert-circle" class="mr-2" color="error" v-else-if="isFailed"></v-icon>
      <v-icon icon="mdi-file-document" class="mr-2" v-else></v-icon>
      {{ title }}
    </v-card-title>

    <v-card-text class="pa-4">
      <v-row>
        <!-- Left Column - Progress Steps -->
        <v-col cols="12" md="4" class="pr-md-4">
          <div class="progress-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="step.value"
          class="step-item d-flex align-center mb-3"
        >
          <v-avatar
            :size="40"
            :color="getStepColor(index + 1)"
            class="mr-3"
          >
            <v-icon
              :color="getStepColor(index + 1) === 'surface-variant' ? 'on-surface-variant' : 'white'"
              :icon="getStepIcon(index + 1, step)"
            ></v-icon>
          </v-avatar>
          <div class="flex-grow-1">
            <div class="text-body-1 font-weight-medium">{{ step.title }}</div>
            <div class="text-caption" :class="getStepTextClass(index + 1)">
              {{ getStepText(index + 1) }}
            </div>
          </div>
        </div>
          </div>
        </v-col>

        <!-- Right Column - Progress Circle -->
        <v-col cols="12" md="8" class="pl-md-4">
          <div class="d-flex flex-column align-center">
            <!-- Progress Circle -->
            <v-progress-circular
              :model-value="progressPercentage"
              :size="120"
              :width="8"
              :color="progressColor"
              class="progress-circle mb-4"
            >
              <div class="text-center">
                <div class="text-h6 font-weight-bold">{{ progressPercentage }}%</div>
                <div class="text-caption text-medium-emphasis" v-if="estimatedTimeRemaining">
                  {{ formatTime(estimatedTimeRemaining) }} left
                </div>
              </div>
            </v-progress-circular>

            <!-- Current Step -->
            <v-chip
              :color="statusColor"
              variant="tonal"
              class="mb-4"
              prepend-icon="mdi-clock-outline"
            >
              {{ currentStep }}
            </v-chip>
          </div>
        </v-col>
      </v-row>

      <!-- Time Information -->
      <div class="d-flex justify-space-between align-center mt-4 pa-3 bg-surface-variant rounded">
        <div class="text-center">
          <div class="text-caption text-high-emphasis font-weight-medium">Elapsed</div>
          <div class="text-body-2 font-weight-bold">{{ formatTime(elapsedTime) }}</div>
        </div>
        <v-divider vertical></v-divider>
        <div class="text-center" v-if="estimatedTimeRemaining">
          <div class="text-caption text-high-emphasis font-weight-medium">Remaining</div>
          <div class="text-body-2 font-weight-bold">{{ formatTime(estimatedTimeRemaining) }}</div>
        </div>
        <div class="text-center" v-else>
          <div class="text-caption text-high-emphasis font-weight-medium">Status</div>
          <div class="text-body-2 font-weight-bold">{{ statusText }}</div>
        </div>
      </div>

      <!-- Error Message -->
      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        class="mt-4"
        :text="error"
      ></v-alert>

      <!-- Success Message -->
      <v-alert
        v-if="isCompleted && !error"
        type="success"
        variant="tonal"
        class="mt-4"
        text="Resume generation completed successfully!"
      ></v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useResumeStore } from '@/store/resume'

const resumeStore = useResumeStore()

const props = defineProps<{
  title?: string
}>()

// Computed properties from store
const isGenerating = computed(() => resumeStore.isGenerating)
const isCompleted = computed(() => resumeStore.isCompleted)
const isFailed = computed(() => resumeStore.isFailed)
const progressPercentage = computed(() => resumeStore.progressPercentage)
const currentStep = computed(() => resumeStore.currentStep)
const estimatedTimeRemaining = computed(() => resumeStore.estimatedTimeRemaining)
const elapsedTime = computed(() => resumeStore.elapsedTime)
const error = computed(() => resumeStore.state.error)

const title = computed(() => {
  if (props.title) return props.title
  if (isCompleted.value) return 'Resume Generated!'
  if (isFailed.value) return 'Generation Failed'
  if (isGenerating.value) return 'Generating Resume...'
  return 'Resume Generation'
})

const progressColor = computed(() => {
  if (isFailed.value) return 'error'
  if (isCompleted.value) return 'success'
  return 'primary'
})

const statusColor = computed(() => {
  if (isFailed.value) return 'error'
  if (isCompleted.value) return 'success'
  return 'primary'
})

const statusText = computed(() => {
  if (isCompleted.value) return 'Complete'
  if (isFailed.value) return 'Failed'
  if (isGenerating.value) return 'Processing'
  return 'Ready'
})

// Steps configuration
const steps = [
  { title: 'Parsing', value: 'parsing', icon: 'mdi-file-search' },
  { title: 'Analyzing', value: 'analyzing', icon: 'mdi-brain' },
  { title: 'Optimizing', value: 'optimizing', icon: 'mdi-tune' },
  { title: 'Constructing', value: 'constructing', icon: 'mdi-hammer-wrench' },
  { title: 'Completed', value: 'completed', icon: 'mdi-check-circle' }
]

const currentStepIndex = computed(() => {
  const status = resumeStore.state.status?.status
  if (!status) return 1
  
  const stepMap: Record<string, number> = {
    'parsing': 1,
    'analyzing': 2,
    'optimizing': 3,
    'constructing': 4,
    'completed': 5,
    'failed': 5
  }
  
  return stepMap[status] || 1
})

function getStepColor(stepNumber: number): string {
  if (isFailed.value && stepNumber === currentStepIndex.value) return 'error'
  if (stepNumber < currentStepIndex.value) return 'success'
  if (stepNumber === currentStepIndex.value) return 'primary'
  return 'surface-variant'
}

function getStepIcon(stepNumber: number, item: any): string {
  if (isFailed.value && stepNumber === currentStepIndex.value) return 'mdi-alert-circle'
  if (stepNumber < currentStepIndex.value) return 'mdi-check-circle'
  return item.icon
}

function getStepText(stepNumber: number): string {
  if (stepNumber === currentStepIndex.value && isGenerating.value) return 'In progress...'
  if (stepNumber <= currentStepIndex.value && (isCompleted.value || isFailed.value)) return 'Completed'
  if (stepNumber < currentStepIndex.value) return 'Completed'
  return 'Pending'
}

function getStepTextClass(stepNumber: number): string {
  if (stepNumber === currentStepIndex.value && isGenerating.value) return 'text-medium-emphasis'
  if (stepNumber < currentStepIndex.value) return 'text-success'
  return 'text-medium-emphasis'
}

function formatTime(seconds: number): string {
  return resumeStore.formatTime(seconds)
}
</script>

<style scoped>
.progress-tracker {
  max-width: 100%;
  width: 100%;
}

.progress-circle {
  position: relative;
}

.rotating {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.step-item {
  transition: all 0.3s ease;
}

.step-item:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.04);
  border-radius: 8px;
  padding: 8px;
  margin: -8px;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .progress-circle {
    transform: scale(0.8);
  }
  
  .step-item .v-avatar {
    width: 32px !important;
    height: 32px !important;
  }
  
  .step-item .text-body-1 {
    font-size: 0.875rem;
  }
}
</style>
