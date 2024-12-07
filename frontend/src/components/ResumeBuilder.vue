<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <v-card class="mx-auto pa-6" elevation="8" rounded="lg">
          <v-card-title class="text-h4 mb-4 d-flex align-center">
            <v-icon icon="mdi-file-document-edit" size="x-large" class="mr-3" color="primary"></v-icon>
            ATS-Friendly Resume Generator
          </v-card-title>

          <v-card-subtitle class="text-body-1 mb-6">
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
              class="mb-6"
              color="primary"
              grow
            >
              <v-tab value="file" class="text-body-1">
                <v-icon icon="mdi-file-upload" class="mr-2"></v-icon>
                Upload File
              </v-tab>
              <v-tab value="text" class="text-body-1">
                <v-icon icon="mdi-clipboard-text" class="mr-2"></v-icon>
                Paste Text
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
                    label="Job Description File"
                    :error-messages="errorMessage"
                    @update:model-value="clearError"
                    variant="outlined"
                    class="mb-4"
                    :class="{ 'elevation-3': isHovering }"
                    density="comfortable"
                    :hint="'Supported formats: .txt, .pdf, .doc, .docx'"
                    persistent-hint
                  >
                    <template v-slot:prepend>
                      <v-tooltip location="top" text="Upload a job description file">
                        <template v-slot:activator="{ props }">
                          <v-icon v-bind="props" icon="mdi-file-document" color="primary"></v-icon>
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
                    label="Job Description Text"
                    placeholder="Paste the job description here"
                    :error-messages="errorMessage"
                    @update:model-value="clearError"
                    variant="outlined"
                    rows="8"
                    class="mb-4"
                    :class="{ 'elevation-3': isHovering }"
                    density="comfortable"
                    :hint="'Copy and paste the job description from any source'"
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
                  size="large"
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

            <v-expand-transition>
              <v-card
                v-if="generatedResume"
                class="mt-6"
                variant="outlined"
                elevation="3"
                rounded="lg"
              >
                <v-card-title class="d-flex align-center pa-4 bg-primary text-white rounded-t-lg">
                  <v-icon icon="mdi-file-check" class="mr-2"></v-icon>
                  Generated Resume
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text class="mt-4">
                  <div class="resume-content">
                    {{ generatedResume }}
                  </div>
                </v-card-text>
                <v-divider></v-divider>
                <v-card-actions class="pa-4">
                  <v-tooltip location="top" text="Copy resume to clipboard">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        v-bind="props"
                        color="primary"
                        variant="tonal"
                        prepend-icon="mdi-content-copy"
                        @click="copyToClipboard"
                        class="mr-2"
                      >
                        Copy to Clipboard
                      </v-btn>
                    </template>
                  </v-tooltip>

                  <v-tooltip location="top" text="Download resume as text file">
                    <template v-slot:activator="{ props }">
                      <v-btn
                        v-bind="props"
                        color="primary"
                        variant="tonal"
                        prepend-icon="mdi-download"
                        @click="downloadResume"
                        class="mr-2"
                      >
                        Download Text
                      </v-btn>
                    </template>
                  </v-tooltip>

                  <v-tooltip location="top" text="Download professional PDF version with watermark">
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

                  <v-snackbar
                    v-model="showCopySuccess"
                    color="success"
                    timeout="2000"
                    location="top"
                  >
                    Resume copied to clipboard!
                  </v-snackbar>
                </v-card-actions>
              </v-card>
            </v-expand-transition>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()

const activeTab = ref('file')
const file = ref<File | null>(null)
const jobDescriptionText = ref('')
const loading = ref(false)
const generatedResume = ref('')
const errorMessage = ref('')
const jobTitle = ref('')
const showCopySuccess = ref(false)
const pdfUrl = ref<string | null>(null)
const pdfLoading = ref(false)

const isInputValid = computed(() => {
  return activeTab.value === 'file' ? !!file.value : !!jobDescriptionText.value.trim()
})

const clearError = () => {
  errorMessage.value = ''
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generatedResume.value)
    showCopySuccess.value = true
  } catch (err) {
    console.error('Failed to copy text: ', err)
  }
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
    const response = await axios.get(`http://localhost:8000${pdfUrl.value}`, {
      responseType: 'blob'
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

  // Add job description
  if (activeTab.value === 'file') {
    formData.append('job_description', file.value!)
  } else {
    const textFile = new Blob([jobDescriptionText.value], { type: 'text/plain' })
    formData.append('job_description', textFile, 'job_description.txt')
  }

  try {
    const response = await axios.post('http://localhost:8000/api/generate-resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    generatedResume.value = response.data.content
    jobTitle.value = response.data.job_title || ''
    pdfUrl.value = response.data.pdf_url || null
  } catch (error: any) {
    errorMessage.value = error.response?.data?.detail || 'Error generating resume. Please try again.'
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.resume-content {
  white-space: pre-wrap;
  font-family: 'Roboto Mono', monospace;
  background-color: rgb(var(--v-theme-surface-variant));
  padding: 16px;
  border-radius: 8px;
  max-height: 400px;
  overflow-y: auto;
  line-height: 1.6;
  font-size: 0.95rem;
}

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

.v-file-input, .v-textarea {
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
