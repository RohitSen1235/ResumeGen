<template>
  <v-card class="progress-tracker" elevation="0" rounded="lg" color="transparent">
    <v-card-text class="pa-4">
      <!-- Title -->
      <div class="text-h6 font-weight-medium text-center mb-4">{{ title }}</div>
      
      <!-- Main content with progress steps and centered circle -->
      <div class="progress-container position-relative mb-4">
        <!-- Progress steps -->
        <div class="progress-steps">
          <div 
            v-for="(step, index) in steps" 
            :key="step.value"
            class="step-item d-flex align-center mb-3"
          >
            <v-avatar
              :size="36"
              :color="getStepColor(index + 1)"
              class="mr-4 elevation-2"
            >
              <v-icon
                :color="getStepColor(index + 1) === 'surface-variant' ? 'on-surface-variant' : 'white'"
                :icon="getStepIcon(index + 1, step)"
                size="small"
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

        <!-- Progress circle centered with right offset -->
        <div class="progress-circle-container">
          <v-progress-circular
            :model-value="progressPercentage"
            :size="160"
            :width="10"
            :color="progressColor"
            class="progress-circle"
          >
            <div class="text-center">
              <div class="text-h6 font-weight-bold">{{ progressPercentage }}%</div>
              <!-- <div class="text-caption text-medium-emphasis" v-if="isGenerating">
                {{ currentStep }}
              </div> -->
            </div>
          </v-progress-circular>
        </div>
      </div>

      <v-divider class="my-4"></v-divider>

      <div class="d-flex justify-space-around align-center text-center">
        <div>
          <div class="text-caption text-medium-emphasis">Elapsed</div>
          <div class="text-body-1 font-weight-bold">{{ formatTime(elapsedTime) }}</div>
        </div>
        <div v-if="isGenerating">
          <div class="text-caption text-medium-emphasis">Remaining</div>
          <div class="text-body-1 font-weight-bold">{{ formatTime(estimatedTimeRemaining || 0) }}</div>
        </div>
        <div v-else>
          <div class="text-caption text-medium-emphasis">Status</div>
          <div class="text-body-1 font-weight-bold">{{ statusText }}</div>
        </div>
      </div>

      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        class="mt-4"
        :text="error"
        density="compact"
        rounded="lg"
      ></v-alert>

      <v-alert
        v-if="isCompleted && !error"
        type="success"
        variant="tonal"
        class="mt-4"
        text="Your resume is ready!"
        density="compact"
        rounded="lg"
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
  width: 100%;
}

.progress-circle {
  transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.step-item {
  transition: all 0.3s ease;
  padding: 8px;
  border-radius: 12px;
}

.step-item:hover {
  background-color: rgba(var(--v-theme-on-surface), 0.05);
}

.text-success {
  color: rgb(var(--v-theme-success));
}

.text-error {
  color: rgb(var(--v-theme-error));
}

.progress-container {
  min-height: 280px; /* Ensure enough height for the circle */
}

.progress-circle-container {
  position: absolute;
  top: 50%;
  left: 60%; /* Center with slight right offset */
  transform: translate(-50%, -50%);
  z-index: 1;
}

.progress-steps {
  position: relative;
  z-index: 2;
  max-width: 50%; /* Limit width to prevent overlap */
}

@media (max-width: 768px) {
  .progress-container {
    min-height: 200px;
  }
  
  .progress-circle-container {
    left: 50%;
    top: 60%;
  }
  
  .progress-steps {
    max-width: 100%;
  }
  
  .progress-circle {
    transform: translate(-50%, -50%) scale(0.9);
  }
}

@media (max-width: 600px) {
  .progress-container {
    min-height: 180px;
  }
  
  .step-item .v-avatar {
    width: 32px !important;
    height: 32px !important;
  }
  
  .step-item .text-body-1 {
    font-size: 0.9rem;
  }
  
  .progress-circle {
    transform: translate(-50%, -50%) scale(0.8);
  }
  
  .progress-circle-container {
    top: 65%;
  }
}
</style>
