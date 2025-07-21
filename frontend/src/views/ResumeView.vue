<template>
  <v-container class="fill-height pa-0" fluid>
    <v-row align="center" justify="center" class="ma-0">
      <v-col cols="12" sm="10" md="8" class="pa-2 pa-sm-4">
        <v-card class="mx-auto pa-6" elevation="8" rounded="lg">
          <v-card-title class="text-h4 mb-4 d-flex align-center">
            <v-icon icon="mdi-file-account" class="mr-2"></v-icon>
            Resume Preview
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-arrow-left"
              @click="$router.go(-1)"
              class="mr-2"
            >
              Back
            </v-btn>
          </v-card-title>

          <v-card-text>
            <v-btn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-pencil"
              @click="isEditing = !isEditing"
              class="mb-4"
            >
              {{ isEditing ? 'Save' : 'Edit' }}
            </v-btn>

            <v-textarea
              v-if="isEditing"
              v-model="resumeContent"
              variant="plain"
              auto-grow
              rows="10"
              class="resume-editor"
              hide-details
            />

            <div 
              v-else 
              class="resume-preview" 
              v-html="formattedResumeContent"
            />

            <v-divider class="my-4"></v-divider>

            <div class="d-flex gap-2">
              <v-btn
                color="primary"
                variant="tonal"
                prepend-icon="mdi-file-pdf-box"
                @click="downloadPdf"
                :loading="pdfLoading"
              >
                Download PDF
              </v-btn>

              <v-btn
                color="primary"
                variant="tonal"
                prepend-icon="mdi-file-word"
                @click="downloadDocx"
                :loading="docxLoading"
              >
                Download Word
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { marked } from 'marked'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const route = useRoute()

const resumeContent = ref('')
const isEditing = ref(false)
const pdfLoading = ref(false)
const docxLoading = ref(false)

const formattedResumeContent = computed(() => {
  return marked(resumeContent.value, { breaks: true })
})

const fetchResume = async () => {
  try {
    const response = await axios.get(`/api/resume/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    resumeContent.value = response.data.content
  } catch (error) {
    console.error('Error fetching resume:', error)
  }
}

const downloadPdf = async () => {
  try {
    pdfLoading.value = true
    const response = await axios.post('/generate-pdf', {
      content: resumeContent.value
    }, {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    // Download the PDF
    const pdfResponse = await axios.get(response.data.pdf_url, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    const url = window.URL.createObjectURL(new Blob([pdfResponse.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `resume-${route.params.id}.pdf`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Error downloading PDF:', error)
  } finally {
    pdfLoading.value = false
  }
}

const downloadDocx = async () => {
  try {
    docxLoading.value = true
    const response = await axios.post('/generate-resume-docx', {
      content: resumeContent.value
    }, {
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    // Download the DOCX
    const docxResponse = await axios.get(response.data.docx_url, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${auth.token}`
      }
    })
    
    const url = window.URL.createObjectURL(new Blob([docxResponse.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `resume-${route.params.id}.docx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    console.error('Error downloading Word document:', error)
  } finally {
    docxLoading.value = false
  }
}

onMounted(() => {
  fetchResume()
})
</script>

<style scoped>
.resume-preview {
  width: 100%;
  max-width: 100%;
  padding: 16px;
  max-height: 600px;
  overflow-y: auto;
  overflow-x: hidden;
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  box-sizing: border-box;
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  font-size: 0.95rem;
}

.resume-editor {
  font-family: 'Roboto', sans-serif;
  background-color: rgb(var(--v-theme-surface));
  border-radius: 8px;
  padding: 16px;
  line-height: 1.6;
  font-size: 0.95rem;
  width: 100%;
  min-height: 600px;
}

@media (max-width: 675px) {
  .resume-preview, .resume-editor {
    max-height: 400px;
    padding: 8px;
    font-size: 0.8rem;
  }
}
</style>
