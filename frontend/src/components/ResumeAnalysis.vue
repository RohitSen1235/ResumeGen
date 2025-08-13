<template>
  <v-card class="h-100" elevation="0" rounded="lg" color="transparent">
    <v-card-text class="pa-0">
      <v-tabs 
        v-model="activeAnalysisTab" 
        color="primary"
        grow
        density="comfortable"
        class="mb-4"
      >
        <v-tab value="summary" class="text-subtitle-2">
          <v-icon icon="mdi-view-dashboard-outline" class="mr-2"></v-icon>
          Summary
        </v-tab>
        <v-tab value="detailed" class="text-subtitle-2">
          <v-icon icon="mdi-text-box-search-outline" class="mr-2"></v-icon>
          Detailed Analysis
        </v-tab>
      </v-tabs>

      <v-window v-model="activeAnalysisTab" class="analysis-content">
        <v-window-item value="summary" class="pa-2">
          <div v-if="analysisSummary" class="summary-content">
            <div v-html="formattedSummary" class="analysis-html"></div>
          </div>
          <div v-else class="text-center pa-8">
            <v-icon icon="mdi-information-outline" size="56" color="grey-lighten-1" class="mb-4"></v-icon>
            <h4 class="text-h6">No Summary Available</h4>
            <p class="text-body-2 text-medium-emphasis mt-2">
              The analysis summary will be shown here once your resume is generated.
            </p>
          </div>
        </v-window-item>

        <v-window-item value="detailed" class="pa-2">
          <div v-if="agentOutputs" class="detailed-analysis">
            <div v-html="formattedAnalysis" class="analysis-html"></div>
          </div>
          <div v-else class="text-center pa-8">
            <v-icon icon="mdi-text-box-search-outline" size="56" color="grey-lighten-1" class="mb-4"></v-icon>
            <h4 class="text-h6">No Detailed Analysis</h4>
            <p class="text-body-2 text-medium-emphasis mt-2">
              A detailed breakdown from our AI will appear here.
            </p>
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
  analysisSummary?: string
}

const props = defineProps<Props>()

const activeAnalysisTab = ref('summary')

// Format the detailed analysis
const formattedAnalysis = computed(() => {
  if (!props.agentOutputs) return ''
  return marked(props.agentOutputs, { breaks: true })
})

// Format the summary analysis
const formattedSummary = computed(() => {
  if (!props.analysisSummary) return ''
  return marked(props.analysisSummary, { breaks: true })
})
</script>

<style scoped>
.analysis-content {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  padding: 4px;
}

.analysis-html {
  font-size: 0.9rem;
  line-height: 1.7;
  color: #424242;
}

.analysis-html :deep(h1),
.analysis-html :deep(h2),
.analysis-html :deep(h3) {
  color: #1E88E5; /* Primary color */
  margin-top: 1.8rem;
  margin-bottom: 0.8rem;
  font-weight: 600;
  border-bottom: 1px solid #E0E0E0;
  padding-bottom: 0.4rem;
}

.analysis-html :deep(h1) { font-size: 1.3rem; }
.analysis-html :deep(h2) { font-size: 1.2rem; }
.analysis-html :deep(h3) { font-size: 1.1rem; }

.analysis-html :deep(p) {
  margin-bottom: 1rem;
}

.analysis-html :deep(ul) {
  margin-bottom: 1.2rem;
  padding-left: 1.5rem;
}

.analysis-html :deep(li) {
  margin-bottom: 0.5rem;
}

.analysis-html :deep(strong) {
  color: #0D47A1; /* Darker primary */
  font-weight: 600;
}

.analysis-html :deep(em) {
  color: #42A5F5; /* Lighter primary */
  font-style: italic;
}

.analysis-html :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-radius: 8px;
  overflow: hidden;
}

.analysis-html :deep(th),
.analysis-html :deep(td) {
  padding: 12px 16px;
  border: none;
  text-align: left;
}

.analysis-html :deep(th) {
  background-color: #1E88E5;
  color: white;
  font-weight: 600;
}

.analysis-html :deep(tr) {
  border-bottom: 1px solid #E0E0E0;
}

.analysis-html :deep(tr:nth-child(even)) {
  background-color: #F5F5F5;
}

.analysis-html :deep(tr:last-child) {
  border-bottom: none;
}

@media (max-width: 600px) {
  .analysis-content {
    max-height: calc(100vh - 180px);
  }
  .analysis-html {
    font-size: 0.85rem;
  }
}
</style>
