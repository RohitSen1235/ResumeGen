<template>
<v-container class="fill-height pa-0">
  <v-row align="center" justify="center" class="ma-0">
    <v-col cols="12" sm="10" md="8" class="pa-2 pa-sm-4">
        <v-card class="mx-auto pa-6" elevation="8" rounded="lg">
          <v-card-title class="text-h4 mb-4 d-flex align-center justify-center">
            <img 
              src="@/assets/logo-dark.svg" 
              alt="Resume-Genie.ai" 
              class="mb-2 mb-sm-4"
              :style="{
                width: $vuetify.display.mobile ? '200px' : '300px',
                height: 'auto'
              }"
            >
          </v-card-title>

          <v-card-subtitle class="text-body-2 text-sm-body-1 mb-4 mb-sm-6 text-center">
            Generate tailored, ATS-optimized resumes using advanced AI technology
          </v-card-subtitle>

          <v-card-text>
            <!-- Job Description Input -->
            <v-alert
              color="info"
              variant="tonal"
              class="mb-6"
              border="start"
              elevation="2"
            >
              <template v-slot:prepend>
                <v-icon icon="mdi-information" class="mr-2"></v-icon>
              </template>
              Choose your preferred method to input the job description. Our AI will analyze it and generate a tailored, ATS-friendly resume.
            </v-alert>

            <v-tabs 
              v-model="activeTab" 
              class="mb-4 mb-sm-6"
              color="primary"
              grow
              :height="$vuetify.display.mobile ? 48 : 56"
            >
              <v-tab value="text" class="text-body-1">
                <v-icon icon="mdi-clipboard-text" class="mr-2"></v-icon>
                Job Description Text
              </v-tab>
              <v-tab value="file" class="text-body-1">
                <v-icon icon="mdi-file-upload" class="mr-2"></v-icon>
                Select File
              </v-tab>
            </v-tabs>

            <v-window v-model="activeTab">
              <v-window-item value="file">
                <v-hover v-slot="{ isHovering, props }">
                  <v-file-input
                    v-bind="props"
                    v-model="file"
                    :rules="[v => !!v || (activeTab === 'file' && 'Job description file is required')]"
                    accept=".txt,.pdf,.doc,.docx"
                    placeholder="Drag and drop a file or click to browse"
                    prepend-icon="mdi-file-document"
                    label="Browse and Add Job Description File"
                    :error-messages="errorMessage"
                    @update:model-value="clearError"
                    variant="outlined"
                    class="mb-4"
                    :class="{ 'elevation-3': isHovering }"
                    density="comfortable"
                    :hint="'Supported formats: .txt'"
                    persistent-hint
                  >
                    <template v-slot:prepend>
                      <v-tooltip location="top" text="Upload a job description file">
                        <template v-slot:activator="{ props }">
                        </template>
                      </v-tooltip>
                    </template>
                  </v-file-input>
                </v-hover>
              </v-window-item>

              <v-window-item value="text">
                <v-hover v-slot="{ isHovering, props }">
                  <v-textarea
                    v-bind="props"
                    v-model="jobDescriptionText"
                    :rules="[v => !!v || (activeTab === 'text' && 'Job description text is required')]"
                    label="Type Job Description Text"
                    placeholder="Paste the job description here"
                    :error-messages="errorMessage"
                    @update:model-value="clearError"
                    variant="outlined"
                    :rows="$vuetify.display.mobile ? 5 : 8"
                    class="mb-4"
                    :class="{ 'elevation-3': isHovering }"
                    density="comfortable"
                    :hint="'Copy and Paste the job description from any source (Linkedin , Naukri ...)'"
                    persistent-hint
                  >
                    <template v-slot:prepend>
                      <v-tooltip location="top" text="Paste job description text">
                        <template v-slot:activator="{ props }">
                          <v-icon v-bind="props" icon="mdi-clipboard-text" color="primary"></v-icon>
                        </template>
                      </v-tooltip>
                    </template>
                  </v-textarea>
                </v-hover>
              </v-window-item>
            </v-window>

            <v-tooltip
              location="top"
              text="Generate an ATS-optimized resume based on the job description"
            >
              <template v-slot:activator="{ props }">
                  <v-btn
                    v-bind="props"
                    color="primary"
                    :size="$vuetify.display.mobile ? 'default' : 'large'"
                    block
                    :loading="loading"
                    :disabled="!isInputValid"
                    @click="generateResume"
                    class="mt-4 elevation-2"
                    rounded="lg"
                  >
                  <template v-slot:prepend>
                    <v-icon icon="mdi-magic-staff"></v-icon>
                  </template>
                  {{ loading ? 'Generating Resume...' : 'Generate Resume' }}
                </v-btn>
              </template>
            </v-tooltip>

            <!-- Resume Display Section -->
            <v-expand-transition>
                <v-card
                  v-if="generatedResume"
                  class="mt-4 mt-sm-6 resume-card"
                  variant="outlined"
                  elevation="3"
                  rounded="lg"
                  style="max-width: 100%; width: 100%; overflow-x: hidden;"
                >
                <v-card-title class="d-flex align-center pa-4 bg-primary text-white rounded-t-lg">
                  <v-icon icon="mdi-file-check" class="mr-2"></v-icon>
                  AI-Optimized Resume
                </v-card-title>
                
                <v-tabs v-model="viewTab" color="primary" grow :height="$vuetify.display.mobile ? 48 : 56">
                  <v-tab value="preview">
                    <v-icon icon="mdi-eye" class="mr-2"></v-icon>
                    Resume Preview
                  </v-tab>
                  <v-tab value="raw">
                    <v-icon icon="mdi-code-tags" class="mr-2"></v-icon>
                    Resume Analysis
                  </v-tab>
                </v-tabs>

                <v-divider></v-divider>

                <v-window v-model="viewTab" class="resume-container">
                  <v-window-item value="preview" class="resume-container">
                    <v-card-text class="mt-4 resume-container">
                      <div class="resume-preview" v-html="formattedResumeContent"></div>
                    </v-card-text>
                  </v-window-item>
                  
                  <v-window-item value="raw" class="resume-container">
                    <v-card-text class="mt-4 resume-container">
                      <div class="resume-content" v-html="formattedAgentOutputs"></div>
                    </v-card-text>
                  </v-window-item>
                </v-window>

                <v-divider></v-divider>

                <v-card-actions class="pa-4">
                  <div class="d-flex gap-2">
                    <v-tooltip location="top" text="Download professional PDF version">
                      <template v-slot:activator="{ props }">
                        <v-btn
                          v-if="pdfUrl"
                          v-bind="props"
                          color="primary"
                          variant="tonal"
                          prepend-icon="mdi-file-pdf-box"
                          @click="downloadPdf"
                          :loading="pdfLoading"
                        >
                          Download PDF
                        </v-btn>
                      </template>
                    </v-tooltip>

                    <v-tooltip location="top" text="Download Word document version">
                      <template v-slot:activator="{ props }">
                        <v-btn
                          v-bind="props"
                          color="primary"
                          variant="tonal"
                          prepend-icon="mdi-file-word"
                          @click="downloadDocx"
                          :loading="docxLoading"
                          :disabled="!generatedResume"
                        >
                          Download Word
                        </v-btn>
                      </template>
                    </v-tooltip>
                  </div>

                  <v-spacer></v-spacer>

                  <!-- Token Usage Information -->
                  <v-tooltip location="top" text="View API usage and cost information">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        v-if="tokenUsage"
                        v-bind="props"
                        color="info"
                        variant="text"
                        prepend-icon="mdi-chart-bar"
                        @click="showUsageDialog = true"
                      >
                        View Cost & Usage
                      </v-btn>
                    </template>
                  </v-tooltip>
                </v-card-actions>
              </v-card>
            </v-expand-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Skills Selection Dialog -->
    <v-dialog v-model="showSkillsDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5 bg-primary text-white pa-4">
          <v-icon icon="mdi-tools" class="mr-2"></v-icon>
          Select Skills
        </v-card-title>
        <v-card-text class="pa-4">
          <v-list v-if="parsedSkills.length">
            <v-list-item
              v-for="skill in parsedSkills"
              :key="skill"
            >
              <v-list-item-title>
                <v-checkbox
                  v-model="selectedSkills"
                  :label="skill"
                  :value="skill"
                ></v-checkbox>
              </v-list-item-title>
            </v-list-item>
          </v-list>
          <div v-else>No skills found in the uploaded resume.</div>
        </v-card-text>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="primary" variant="tonal" @click="showSkillsDialog = false">
            Apply Skills
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Token Usage Dialog -->
    <v-dialog v-model="showUsageDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5 bg-primary text-white pa-4">
          <v-icon icon="mdi-chart-bar" class="mr-2"></v-icon>
          Cost & Usage Details
        </v-card-title>
        
        <v-card-text class="pa-4">
          <template v-if="totalUsage">
            <v-list>
              <v-list-item>
                <v-list-item-title class="text-h6 mb-4">Token Usage Summary</v-list-item-title>
                <v-list-item-subtitle>
                  <div class="d-flex justify-space-between align-center mb-3">
                    <span>Total Input Tokens:</span>
                    <span class="font-weight-medium">
                      {{ totalUsage.total_input_tokens + totalUsage.agent_input_tokens }}
                    </span>
                  </div>
                  <div class="d-flex justify-space-between align-center mb-3">
                    <span>Total Output Tokens:</span>
                    <span class="font-weight-medium">
                      {{ totalUsage.total_output_tokens + totalUsage.agent_output_tokens }}
                    </span>
                  </div>
                  <v-divider class="my-3"></v-divider>
                  <div class="d-flex justify-space-between align-center mb-3">
                    <span>Total Cost:</span>
                    <span class="font-weight-medium">₹{{ totalUsage.total_cost.toFixed(2) }}</span>
                  </div>
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </template>
        </v-card-text>

        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            variant="tonal"
            @click="showUsageDialog = false"
          >
            Close
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
})
import { marked } from 'marked'

const auth = useAuthStore()

const activeTab = ref('file')
const viewTab = ref('preview')
const file = ref<File | null>(null)
const jobDescriptionText = ref('')
const loading = ref(false)
const generatedResume = ref('')
const agentOutputs = ref('')
const errorMessage = ref('')
const jobTitle = ref('')
const pdfUrl = ref<string | null>(null)
const docxUrl = ref<string | null>(null)
const pdfLoading = ref(false)
const docxLoading = ref(false)
const showUsageDialog = ref(false)
const showSkillsDialog = ref(false)
const parsedSkills = ref<string[]>([])
const selectedSkills = ref<string[]>([])
const tokenUsage = ref<any>(null)
const totalUsage = ref<any>(null)

const formattedResumeContent = computed(() => {
  if (!generatedResume.value) return ''
  return marked(generatedResume.value, { breaks: true })
})

const formattedAgentOutputs = computed(() => {
  if (!agentOutputs.value) return ''
  return marked(agentOutputs.value, { breaks: true })
})

const isInputValid = computed(() => {
  return activeTab.value === 'file' ? !!file.value : !!jobDescriptionText.value.trim()
})

const clearError = () => {
  errorMessage.value = ''
}

const downloadResume = () => {
  const blob = new Blob([generatedResume.value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const filename = jobTitle.value ? 
    `resume-${jobTitle.value}-${new Date().toISOString().split('T')[0]}.txt` : 
    `resume-${new Date().toISOString().split('T')[0]}.txt`
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

const downloadPdf = async () => {
  if (!pdfUrl.value) return
  
  try {
    pdfLoading.value = true
    const response = await apiClient.get(`${pdfUrl.value}`, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    const filename = jobTitle.value ?
      `resume-${jobTitle.value}-${new Date().toISOString().split('T')[0]}.pdf` :
      `resume-${new Date().toISOString().split('T')[0]}.pdf`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error downloading PDF:', error)
    errorMessage.value = 'Error downloading PDF. Please try again.'
  } finally {
    pdfLoading.value = false
  }
}

const downloadDocx = async () => {
  if (!generatedResume.value) return
  
  try {
    docxLoading.value = true
    // First generate the DOCX file
    const generateResponse = await apiClient.post('/generate-resume-docx', {
      ai_content: generatedResume.value,
      job_title: jobTitle.value
    }, {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    // Then download the generated DOCX
    const downloadResponse = await apiClient.get(generateResponse.data.docx_url, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    const url = window.URL.createObjectURL(new Blob([downloadResponse.data]))
    const link = document.createElement('a')
    link.href = url
    const filename = jobTitle.value ?
      `resume-${jobTitle.value}-${new Date().toISOString().split('T')[0]}.docx` :
      `resume-${new Date().toISOString().split('T')[0]}.docx`
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error generating/downloading Word document:', error)
    errorMessage.value = 'Error generating Word document. Please try again.'
  } finally {
    docxLoading.value = false
  }
}

const generateResume = async () => {
  if (!auth.user?.profile) {
    errorMessage.value = 'Please complete your profile first'
    return
  }

  if (activeTab.value === 'file' && !file.value) {
    errorMessage.value = 'Please select a job description file'
    return
  }

  if (activeTab.value === 'text' && !jobDescriptionText.value.trim()) {
    errorMessage.value = 'Please enter the job description text'
    return
  }

  loading.value = true
  const formData = new FormData()

  if (activeTab.value === 'file') {
    formData.append('job_description', file.value!)
  } else {
    const textFile = new Blob([jobDescriptionText.value], { type: 'text/plain' })
    formData.append('job_description', textFile, 'job_description.txt')
  }

  try {
    const response = await apiClient.post('/generate-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${auth.token}`
      },
    });
    generatedResume.value = response.data.content;
    agentOutputs.value = response.data.agent_outputs || '';
    jobTitle.value = response.data.job_title || '';
    pdfUrl.value = response.data.pdf_url || null;
    docxUrl.value = null; // Reset DOCX URL since we generate on demand now
    tokenUsage.value = response.data.token_usage || null;
    totalUsage.value = response.data.total_usage || null;
    parsedSkills.value = response.data.skills || [];
    viewTab.value = 'preview';
    showSkillsDialog.value = parsedSkills.value.length > 0;
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Error generating resume. Please try again.';
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
}
</script>
<style scoped>
/* Mobile-first responsive styles */
@media (max-width: 600px) {
  .v-card {
    padding: 12px !important;
    margin: 0 !important;
  }
  
  .v-card-title {
    font-size: 1.5rem !important;
  }

  .v-card-subtitle {
    font-size: 0.9rem !important;
  }

  img {
    max-width: 200px !important;
    height: auto !important;
  }

  .v-btn {
    font-size: 0.9rem !important;
    padding: 0 12px !important;
  }

  .v-tabs {
    font-size: 0.8rem !important;
  }
}

/* Base styles for content containers */
.resume-content, .resume-preview {
  width: 100%;
  max-width: 100%;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
  overflow-x: hidden;
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  box-sizing: border-box;
}

/* Ensure consistent width for parent containers */
.v-container {
  width: 100% !important;
  max-width: 100% !important;
  padding: 8px !important;
}

.v-window,
.v-window-item,
.v-card,
.v-card-text {
  width: 100% !important;
  max-width: 100% !important;
  overflow-x: hidden !important;
  box-sizing: border-box !important;
}

@media (max-width: 600px) {
  .v-col {
    padding: 0 !important;
  }
  
  .v-card-text {
    padding: 12px !important;
  }
  
  .v-textarea, .v-file-input {
    font-size: 0.9rem !important;
  }
}

/* Specific styles for resume content and preview */
.resume-content, .resume-preview {
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  font-size: 0.95rem;
  width: 100%;
  overflow: auto;
}

@media (max-width: 600px) {
  .resume-content, .resume-preview {
    font-size: 0.85rem;
    padding: 8px;
  }
  
  .resume-preview :deep(h1) {
    font-size: 1.2rem;
  }
  
  .resume-preview :deep(h2) {
    font-size: 1.1rem;
  }
  
  .resume-preview :deep(p),
  .resume-preview :deep(li) {
    font-size: 0.9rem;
  }
  
  .resume-preview :deep(ul) {
    padding-left: 1rem;
  }
}

/* Force all nested elements to respect container width */
.resume-preview :deep(*),
.resume-content :deep(*) {
  max-width: 100% !important;
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: normal;
  box-sizing: border-box;
}

.resume-preview :deep(table) {
  width: 100% !important;
  display: block;
  overflow-x: auto;
}

.resume-preview :deep(img) {
  max-width: 100% !important;
  height: auto !important;
}

/* Specific element styles in preview */
.resume-preview :deep(p),
.resume-preview :deep(div),
.resume-preview :deep(span) {
  margin: 0 0 1rem 0;
}

.resume-preview :deep(h1) {
  font-size: 1.5rem;
  color: rgb(var(--v-theme-primary));
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 500;
}

.resume-preview :deep(ul) {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 1rem;
  max-width: calc(100% - 1.5rem);
}

.resume-preview :deep(li) {
  margin-bottom: 0.5rem;
}

/* Project section specific styles */
.resume-preview :deep(li strong) {
  color: rgb(var(--v-theme-primary));
  font-weight: 500;
}

.resume-preview :deep(li em) {
  color: rgba(var(--v-theme-on-surface), 0.7);
  font-style: italic;
}

/* Container constraints */
.v-window,
.v-window-item,
.v-card,
.v-card-text {
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
  box-sizing: border-box;
}

@media (max-width: 600px) {
  .resume-content, .resume-preview {
    max-height: 300px;
    padding: 12px;
    font-size: 0.9rem;
  }
  
  .v-dialog {
    width: 95% !important;
    margin: 8px !important;
  }
}

/* Additional UI styles */
.v-card {
  transition: transform 0.2s ease-in-out;
}

.v-card:hover {
  transform: translateY(-2px);
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.v-file-input,
.v-textarea {
  transition: all 0.2s ease-in-out;
}

:deep(.v-field) {
  border-radius: 8px;
}

.v-card-title {
  letter-spacing: 0.5px;
}

.v-alert {
  border-radius: 8px;
}
</style>
