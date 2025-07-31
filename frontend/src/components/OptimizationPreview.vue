<template>
  <v-card class="optimization-preview" elevation="3" rounded="lg">
    <v-card-title class="d-flex align-center pa-4 bg-secondary text-white rounded-t-lg">
      <v-icon icon="mdi-lightbulb" class="mr-2"></v-icon>
      Key Improvements
    </v-card-title>

    <v-card-text class="pa-4">
      <!-- Loading State -->
      <div v-if="isGenerating && !improvements.length" class="text-center py-8">
        <v-progress-circular indeterminate color="primary" class="mb-4"></v-progress-circular>
        <div class="text-body-1 text-medium-emphasis">Analyzing your resume...</div>
      </div>

      <!-- Improvements List -->
      <div v-else-if="improvements.length" class="improvements-list">
        <v-timeline density="compact" side="end">
          <v-timeline-item
            v-for="(improvement, index) in improvements"
            :key="index"
            :dot-color="improvement.type === 'success' ? 'success' : improvement.type === 'warning' ? 'warning' : 'info'"
            size="small"
          >
            <template v-slot:icon>
              <v-icon :icon="getImprovementIcon(improvement.type)" size="small"></v-icon>
            </template>
            
            <v-card variant="tonal" :color="improvement.type === 'success' ? 'success' : improvement.type === 'warning' ? 'warning' : 'info'" class="mb-3">
              <v-card-text class="pa-3">
                <div class="text-body-2 font-weight-medium mb-1">{{ improvement.title }}</div>
                <div class="text-caption">{{ improvement.description }}</div>
                <v-chip
                  v-if="improvement.impact"
                  :color="getImpactColor(improvement.impact)"
                  size="x-small"
                  variant="flat"
                  class="mt-2"
                >
                  {{ improvement.impact }} Impact
                </v-chip>
              </v-card-text>
            </v-card>
          </v-timeline-item>
        </v-timeline>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-8">
        <v-icon icon="mdi-file-search" size="64" color="surface-variant" class="mb-4"></v-icon>
        <div class="text-body-1 text-medium-emphasis">Start generating to see improvements</div>
      </div>

      <!-- Agent Insights -->
      <div v-if="agentInsights.length" class="mt-6">
        <v-divider class="mb-4"></v-divider>
        <div class="text-h6 mb-3">AI Agent Insights</div>
        <v-expansion-panels variant="accordion">
          <v-expansion-panel
            v-for="(insight, index) in agentInsights"
            :key="index"
            :title="insight.agent"
          >
            <v-expansion-panel-text>
              <div class="text-body-2" v-html="formatInsight(insight.content)"></div>
              <v-chip
                v-if="insight.score"
                color="primary"
                size="small"
                variant="tonal"
                class="mt-2"
              >
                Score: {{ insight.score }}/10
              </v-chip>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useResumeStore } from '@/store/resume'

interface Improvement {
  type: 'success' | 'warning' | 'info'
  title: string
  description: string
  impact?: 'High' | 'Medium' | 'Low'
}

interface AgentInsight {
  agent: string
  content: string
  score?: number
}

const resumeStore = useResumeStore()

// Computed properties from store
const isGenerating = computed(() => resumeStore.isGenerating)
const isCompleted = computed(() => resumeStore.isCompleted)
const currentStep = computed(() => resumeStore.currentStep)
const result = computed(() => resumeStore.state.result)

// Mock improvements based on current step
const improvements = computed<Improvement[]>(() => {
  const status = resumeStore.state.status?.status
  const items: Improvement[] = []

  if (status === 'parsing' || (status && ['analyzing', 'optimizing', 'constructing', 'completed'].includes(status))) {
    items.push({
      type: 'success',
      title: 'Job Requirements Identified',
      description: 'Successfully extracted key requirements from the job description',
      impact: 'High'
    })
  }

  if (status === 'analyzing' || (status && ['optimizing', 'constructing', 'completed'].includes(status))) {
    items.push({
      type: 'info',
      title: 'Skills Alignment',
      description: 'Analyzing your skills against job requirements for better matching',
      impact: 'High'
    })
  }

  if (status === 'optimizing' || (status && ['constructing', 'completed'].includes(status))) {
    items.push({
      type: 'success',
      title: 'Content Enhancement',
      description: 'Optimizing experience descriptions with action verbs and quantifiable achievements',
      impact: 'Medium'
    })
    
    items.push({
      type: 'warning',
      title: 'ATS Optimization',
      description: 'Ensuring resume format is compatible with Applicant Tracking Systems',
      impact: 'High'
    })
  }

  if (status === 'constructing' || status === 'completed') {
    items.push({
      type: 'success',
      title: 'Professional Formatting',
      description: 'Applied clean, professional layout optimized for readability',
      impact: 'Medium'
    })
    
    items.push({
      type: 'info',
      title: 'Keyword Integration',
      description: 'Strategically placed relevant keywords throughout the resume',
      impact: 'High'
    })
  }

  return items
})

// Agent insights from the result
const agentInsights = computed<AgentInsight[]>(() => {
  if (!result.value?.agent_outputs) return []

  const insights: AgentInsight[] = []
  const outputs = result.value.agent_outputs

  // Parse agent outputs (this is a simplified version)
  if (outputs.includes('Content Quality')) {
    insights.push({
      agent: 'Content Quality Agent',
      content: 'Analyzed resume content for clarity, impact, and professional presentation.',
      score: 8
    })
  }

  if (outputs.includes('Skills')) {
    insights.push({
      agent: 'Skills Alignment Agent',
      content: 'Evaluated skill matching and identified opportunities for better alignment with job requirements.',
      score: 7
    })
  }

  if (outputs.includes('Experience')) {
    insights.push({
      agent: 'Experience Enhancement Agent',
      content: 'Optimized experience descriptions with quantifiable achievements and action-oriented language.',
      score: 9
    })
  }

  return insights
})

function getImprovementIcon(type: string): string {
  switch (type) {
    case 'success': return 'mdi-check-circle'
    case 'warning': return 'mdi-alert-circle'
    case 'info': return 'mdi-information'
    default: return 'mdi-circle'
  }
}

function getImpactColor(impact: string): string {
  switch (impact) {
    case 'High': return 'error'
    case 'Medium': return 'warning'
    case 'Low': return 'info'
    default: return 'surface-variant'
  }
}

function formatInsight(content: string): string {
  // Simple formatting for agent insights
  return content.replace(/\n/g, '<br>')
}
</script>

<style scoped>
.optimization-preview {
  max-width: 100%;
  width: 100%;
}

.improvements-list {
  max-height: 400px;
  overflow-y: auto;
}

.v-timeline :deep(.v-timeline-item__body) {
  padding-bottom: 0;
}

.v-timeline :deep(.v-timeline-item__opposite) {
  display: none;
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .v-card-text {
    padding: 12px !important;
  }
  
  .improvements-list {
    max-height: 300px;
  }
  
  .v-timeline :deep(.v-timeline-item__body) {
    padding-left: 12px;
  }
}

/* Custom scrollbar for improvements list */
.improvements-list::-webkit-scrollbar {
  width: 4px;
}

.improvements-list::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 2px;
}

.improvements-list::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-primary), 0.5);
  border-radius: 2px;
}

.improvements-list::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-primary), 0.7);
}
</style>
