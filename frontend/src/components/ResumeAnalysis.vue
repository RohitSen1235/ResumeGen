<template>
  <v-card class="h-100" elevation="2" rounded="lg">
    <v-card-title class="text-h6 bg-primary text-white pa-4">
      <v-icon icon="mdi-chart-line" class="mr-2"></v-icon>
      Resume Analysis
    </v-card-title>
    
    <v-card-text class="pa-0">
      <v-tabs 
        v-model="activeAnalysisTab" 
        color="primary"
        grow
        density="compact"
      >
        <v-tab value="overview" class="text-body-2">
          <v-icon icon="mdi-eye" size="small" class="mr-1"></v-icon>
          Overview
        </v-tab>
        <v-tab value="detailed" class="text-body-2">
          <v-icon icon="mdi-file-document-outline" size="small" class="mr-1"></v-icon>
          Detailed Analysis
        </v-tab>
      </v-tabs>

      <v-window v-model="activeAnalysisTab" class="analysis-content">
        <!-- Overview Tab -->
        <v-window-item value="overview" class="pa-4">
          <div v-if="analysisScores.length > 0">
            <!-- Score Cards -->
            <v-row dense class="mb-4">
              <v-col 
                v-for="score in analysisScores" 
                :key="score.category"
                cols="12" 
                sm="4"
              >
                <v-card variant="outlined" class="text-center pa-2">
                  <v-card-text class="pa-2">
                    <div class="text-h6 mb-1" :class="getScoreColor(score.value)">
                      {{ score.value }}/10
                    </div>
                    <div class="text-caption">{{ score.category }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>

            <!-- Overall Score -->
            <v-card variant="tonal" color="primary" class="mb-4">
              <v-card-text class="text-center pa-3">
                <div class="text-h5 mb-1">
                  Overall Score: {{ overallScore }}/10
                </div>
                <div class="text-body-2">
                  {{ getScoreDescription(overallScore) }}
                </div>
              </v-card-text>
            </v-card>

            <!-- Key Insights -->
            <v-card variant="outlined" class="mb-4">
              <v-card-title class="text-body-1 pa-3">
                <v-icon icon="mdi-lightbulb" class="mr-2" color="amber"></v-icon>
                Key Insights
              </v-card-title>
              <v-card-text class="pa-3">
                <v-list density="compact">
                  <v-list-item 
                    v-for="insight in keyInsights" 
                    :key="insight"
                    class="pa-1"
                  >
                    <template v-slot:prepend>
                      <v-icon icon="mdi-check-circle" color="success" size="small"></v-icon>
                    </template>
                    <v-list-item-title class="text-body-2">{{ insight }}</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </div>

          <div v-else class="text-center pa-4">
            <v-icon icon="mdi-information" size="48" color="info" class="mb-2"></v-icon>
            <div class="text-body-1 mb-2">No Analysis Available</div>
            <div class="text-body-2 text-medium-emphasis">
              Analysis data will appear here after resume generation.
            </div>
          </div>
        </v-window-item>

        <!-- Detailed Analysis Tab -->
        <v-window-item value="detailed" class="pa-4">
          <div v-if="agentOutputs" class="detailed-analysis">
            <div v-html="formattedAnalysis" class="analysis-content"></div>
          </div>
          <div v-else class="text-center pa-4">
            <v-icon icon="mdi-file-document" size="48" color="info" class="mb-2"></v-icon>
            <div class="text-body-1 mb-2">No Detailed Analysis Available</div>
            <div class="text-body-2 text-medium-emphasis">
              Detailed analysis from AI agents will appear here after resume generation.
            </div>
          </div>
        </v-window-item>
      </v-window>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'

interface Props {
  agentOutputs?: string
}

const props = defineProps<Props>()

const activeAnalysisTab = ref('overview')

// Parse analysis scores from agent outputs
const analysisScores = computed(() => {
  if (!props.agentOutputs) return []
  
  const scores = []
  const text = props.agentOutputs
  
  // Extract quality score
  const qualityMatch = text.match(/quality score[:\s]*(\d+(?:\.\d+)?)/i)
  if (qualityMatch) {
    scores.push({
      category: 'Content Quality',
      value: Math.round(parseFloat(qualityMatch[1]))
    })
  }
  
  // Extract skills match score
  const skillsMatch = text.match(/skills match score[:\s]*(\d+(?:\.\d+)?)/i)
  if (skillsMatch) {
    scores.push({
      category: 'Skills Match',
      value: Math.round(parseFloat(skillsMatch[1]))
    })
  }
  
  // Extract experience quality score
  const experienceMatch = text.match(/experience quality score[:\s]*(\d+(?:\.\d+)?)/i)
  if (experienceMatch) {
    scores.push({
      category: 'Experience Quality',
      value: Math.round(parseFloat(experienceMatch[1]))
    })
  }
  
  return scores
})

// Calculate overall score
const overallScore = computed(() => {
  if (analysisScores.value.length === 0) return 0
  const total = analysisScores.value.reduce((sum, score) => sum + score.value, 0)
  return Math.round(total / analysisScores.value.length)
})

// Extract key insights
const keyInsights = computed(() => {
  if (!props.agentOutputs) return []
  
  const insights = []
  const text = props.agentOutputs
  
  // Look for improvement suggestions and positive points
  const lines = text.split('\n')
  const insightLines = lines.filter(line => {
    const lowerLine = line.toLowerCase()
    return (
      (lowerLine.includes('improved') || 
       lowerLine.includes('enhanced') || 
       lowerLine.includes('optimized') ||
       lowerLine.includes('strong') ||
       lowerLine.includes('effective') ||
       lowerLine.includes('well-structured')) &&
      line.length > 20 &&
      line.length < 150
    )
  })
  
  // Take first 3-4 insights
  return insightLines.slice(0, 4).map(line => line.replace(/^[•\-*]\s*/, '').trim())
})

// Format the detailed analysis
const formattedAnalysis = computed(() => {
  if (!props.agentOutputs) return ''
  return marked(props.agentOutputs, { breaks: true })
})

// Helper functions
const getScoreColor = (score: number) => {
  if (score >= 8) return 'text-success'
  if (score >= 6) return 'text-warning'
  return 'text-error'
}

const getScoreDescription = (score: number) => {
  if (score >= 9) return 'Excellent - Your resume is highly optimized'
  if (score >= 8) return 'Very Good - Minor improvements possible'
  if (score >= 7) return 'Good - Some areas for enhancement'
  if (score >= 6) return 'Fair - Several improvements recommended'
  if (score >= 5) return 'Needs Work - Significant improvements needed'
  return 'Poor - Major revisions required'
}

// Watch for changes in agent outputs and switch to overview tab
watch(() => props.agentOutputs, (newValue) => {
  if (newValue && analysisScores.value.length > 0) {
    activeAnalysisTab.value = 'overview'
  }
})
</script>

<style scoped>
.analysis-content {
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.detailed-analysis {
  font-size: 0.9rem;
  line-height: 1.6;
}

.detailed-analysis :deep(h1),
.detailed-analysis :deep(h2),
.detailed-analysis :deep(h3) {
  color: rgb(var(--v-theme-primary));
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.detailed-analysis :deep(h1) {
  font-size: 1.2rem;
}

.detailed-analysis :deep(h2) {
  font-size: 1.1rem;
}

.detailed-analysis :deep(h3) {
  font-size: 1rem;
}

.detailed-analysis :deep(p) {
  margin-bottom: 0.8rem;
}

.detailed-analysis :deep(ul) {
  margin-bottom: 1rem;
  padding-left: 1.2rem;
}

.detailed-analysis :deep(li) {
  margin-bottom: 0.3rem;
}

.detailed-analysis :deep(strong) {
  color: rgb(var(--v-theme-primary));
}

.detailed-analysis :deep(em) {
  color: rgba(var(--v-theme-on-surface), 0.7);
}

/* Mobile responsive */
@media (max-width: 675px) {
  .analysis-content {
    max-height: calc(100vh - 250px);
  }
  
  .detailed-analysis {
    font-size: 0.8rem;
  }
  
  .detailed-analysis :deep(h1) {
    font-size: 1rem;
  }
  
  .detailed-analysis :deep(h2) {
    font-size: 0.95rem;
  }
  
  .detailed-analysis :deep(h3) {
    font-size: 0.9rem;
  }
}

/* Compact styles for small screens */
.v-card-text {
  font-size: 0.85rem;
}

.v-list-item-title {
  font-size: 0.8rem !important;
  line-height: 1.3 !important;
}

@media (max-width: 675px) {
  .v-card-text {
    font-size: 0.75rem;
  }
  
  .v-list-item-title {
    font-size: 0.7rem !important;
  }
  
  .text-h6 {
    font-size: 0.9rem !important;
  }
  
  .text-h5 {
    font-size: 1rem !important;
  }
}
</style>
