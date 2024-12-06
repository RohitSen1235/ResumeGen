<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <v-card class="mx-auto pa-6" elevation="8">
          <v-card-title class="text-h4 mb-4">
            ATS-Friendly Resume Generator
          </v-card-title>

          <v-card-text>
            <v-alert
              color="info"
              variant="tonal"
              class="mb-6"
            >
              Upload a job description file or paste the job description text to generate an ATS-compatible resume.
            </v-alert>

            <v-tabs v-model="activeTab" class="mb-6">
              <v-tab value="file">Upload File</v-tab>
              <v-tab value="text">Paste Text</v-tab>
            </v-tabs>

            <v-window v-model="activeTab">
              <v-window-item value="file">
                <v-file-input
                  v-model="file"
                  :rules="[v => !!v || (activeTab === 'file' && 'Job description file is required')]"
                  accept=".txt,.pdf,.doc,.docx"
                  placeholder="Select a job description file"
                  prepend-icon="mdi-file-document"
                  label="Job Description File"
                  :error-messages="errorMessage"
                  @update:model-value="clearError"
                  variant="outlined"
                  class="mb-4"
                ></v-file-input>
              </v-window-item>

              <v-window-item value="text">
                <v-textarea
                  v-model="jobDescriptionText"
                  :rules="[v => !!v || (activeTab === 'text' && 'Job description text is required')]"
                  label="Job Description Text"
                  placeholder="Paste the job description here"
                  :error-messages="errorMessage"
                  @update:model-value="clearError"
                  variant="outlined"
                  rows="8"
                  class="mb-4"
                ></v-textarea>
              </v-window-item>
            </v-window>

            <v-btn
              color="primary"
              size="large"
              block
              :loading="loading"
              :disabled="!isInputValid"
              @click="generateResume"
              prepend-icon="mdi-file-document-edit"
            >
              Generate Resume
            </v-btn>

            <v-expand-transition>
              <v-card
                v-if="generatedResume"
                class="mt-6"
                variant="outlined"
              >
                <v-card-title class="d-flex align-center">
                  <v-icon icon="mdi-file-check" class="mr-2"></v-icon>
                  Generated Resume
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text class="mt-4">
                  <div class="resume-content">
                    {{ generatedResume }}
                  </div>
                </v-card-text>
                <v-card-actions>
                  <v-btn
                    color="primary"
                    variant="text"
                    prepend-icon="mdi-content-copy"
                    @click="copyToClipboard"
                  >
                    Copy to Clipboard
                  </v-btn>
                  <v-btn
                    color="primary"
                    variant="text"
                    prepend-icon="mdi-download"
                    @click="downloadResume"
                  >
                    Download
                  </v-btn>
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

const activeTab = ref('file')
const file = ref<File | null>(null)
const jobDescriptionText = ref('')
const loading = ref(false)
const generatedResume = ref('')
const errorMessage = ref('')
const jobTitle = ref('')

const isInputValid = computed(() => {
  return activeTab.value === 'file' ? !!file.value : !!jobDescriptionText.value.trim()
})

const clearError = () => {
  errorMessage.value = ''
}

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(generatedResume.value)
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

const generateResume = async () => {
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
    // Create a text file from the input text
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
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
}
</style>
