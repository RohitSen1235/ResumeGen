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
        <v-tab value="summary" class="text-body-2">
          <v-icon icon="mdi-table" size="small" class="mr-1"></v-icon>
          Summary
        </v-tab>
        <v-tab value="detailed" class="text-body-2">
          <v-icon icon="mdi-file-document-outline" size="small" class="mr-1"></v-icon>
          Detailed Analysis
        </v-tab>
      </v-tabs>

      <v-window v-model="activeAnalysisTab" class="analysis-content">
        <!-- Summary Tab -->
        <v-window-item value="summary" class="pa-4">
          <div v-if="analysisSummary" class="summary-content">
            <div v-html="formattedSummary" class="analysis-content"></div>
          </div>
          <div v-else class="text-center pa-4">
            <v-icon icon="mdi-table" size="48" color="info" class="mb-2"></v-icon>
            <div class="text-body-1 mb-2">No Summary Available</div>
            <div class="text-body-2 text-medium-emphasis">
              Summary analysis will appear here after resume generation.
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

/* Summary table styles */
.summary-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.summary-content :deep(th),
.summary-content :deep(td) {
  padding: 0.5rem;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.12);
  text-align: left;
}

.summary-content :deep(th) {
  background-color: rgba(var(--v-theme-primary), 0.1);
}

.summary-content :deep(tr:nth-child(even)) {
  background-color: rgba(var(--v-theme-on-surface), 0.02);
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
