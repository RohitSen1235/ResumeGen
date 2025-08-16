<template>
  <div>
    <v-alert v-if="error" type="error" variant="tonal" class="mb-4" closable @click:close="error = ''">
      {{ error }}
    </v-alert>

    <div v-if="loading" class="text-center py-8">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <div class="mt-4 text-grey-darken-1">Loading your resumes...</div>
    </div>

    <div v-else-if="resumes.length === 0" class="text-center py-8">
      <v-icon icon="mdi-file-document-outline" size="64" color="grey-lighten-1" class="mb-4"></v-icon>
      <div class="text-h6 text-grey-darken-1 mb-2">No resumes found</div>
      <div class="text-body-2 text-grey-darken-2">Generate your first resume to see it here</div>
    </div>

    <v-list v-else class="bg-transparent">
      <v-list-item
        v-for="resume in resumes"
        :key="resume.id"
        class="mb-3"
        rounded="lg"
        elevation="2"
        style="background-color: rgba(255, 255, 255, 0.9);"
      >
        <template v-slot:prepend>
          <v-avatar color="primary" class="mr-3">
            <v-icon icon="mdi-file-document" color="white"></v-icon>
          </v-avatar>
        </template>

        <v-list-item-title class="font-weight-medium text-grey-darken-3">
          {{ resume.name || 'Untitled Resume' }}
        </v-list-item-title>

        <v-list-item-subtitle class="d-flex align-center mt-1">
          <span class="text-grey-darken-1 mr-3">
            {{ formatDate(resume.created_at) }}
          </span>
          <v-chip
            :color="getStatusColor(resume.status)"
            size="x-small"
            variant="flat"
            class="text-caption"
          >
            {{ getStatusText(resume.status) }}
          </v-chip>
        </v-list-item-subtitle>

        <template v-slot:append>
          <div class="d-flex gap-2">
            <v-btn
              color="primary"
              variant="flat"
              size="small"
              prepend-icon="mdi-eye"
              @click="viewResume(resume.id)"
            >
              View
            </v-btn>
            <v-btn
              color="error"
              variant="outlined"
              size="small"
              icon="mdi-delete-outline"
              @click="confirmDelete(resume)"
              :loading="deleteLoading === resume.id"
            ></v-btn>
          </div>
        </template>
      </v-list-item>
    </v-list>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6">
          <v-icon icon="mdi-delete-alert" color="error" class="mr-2"></v-icon>
          Delete Resume
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete "<strong>{{ resumeToDelete?.name || 'Untitled Resume' }}</strong>"?
          <br><br>
          <span class="text-error">This action cannot be undone.</span>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" variant="flat" @click="deleteResume" :loading="deleteLoading">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import axios from 'axios'

const router = useRouter()
const auth = useAuthStore()

// Define emits
const emit = defineEmits<{
  'resume-deleted': []
}>()

// State
const resumes = ref<any[]>([])
const loading = ref(false)
const error = ref('')
const deleteDialog = ref(false)
const resumeToDelete = ref<any>(null)
const deleteLoading = ref('')

// Configure axios
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL
})

apiClient.interceptors.request.use((config) => {
  const token = auth.token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Methods
const fetchResumes = async () => {
  try {
    loading.value = true
    error.value = ''
    
    const response = await apiClient.get('/resumes')
    resumes.value = response.data.slice(0, 10) // Limit to 10 most recent
  } catch (err: any) {
    console.error('Error fetching resumes:', err)
    error.value = 'Failed to load resumes. Please try again.'
  } finally {
    loading.value = false
  }
}

const viewResume = (resumeId: string) => {
  router.push(`/resume/${resumeId}`)
}

const confirmDelete = (resume: any) => {
  resumeToDelete.value = resume
  deleteDialog.value = true
}

const deleteResume = async () => {
  if (!resumeToDelete.value) return

  try {
    deleteLoading.value = resumeToDelete.value.id
    
    await apiClient.delete(`/resumes/${resumeToDelete.value.id}`)
    
    // Remove from local list
    resumes.value = resumes.value.filter(r => r.id !== resumeToDelete.value.id)
    
    // Emit event to parent component
    emit('resume-deleted')
    
    deleteDialog.value = false
    resumeToDelete.value = null
  } catch (err: any) {
    console.error('Error deleting resume:', err)
    error.value = 'Failed to delete resume. Please try again.'
  } finally {
    deleteLoading.value = ''
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'success'
    case 'pending':
      return 'warning'
    case 'failed':
      return 'error'
    default:
      return 'grey'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed':
      return 'Ready'
    case 'pending':
      return 'Processing'
    case 'failed':
      return 'Failed'
    default:
      return 'Unknown'
  }
}

// Expose methods for parent component
defineExpose({
  fetchResumes,
  resumes
})

onMounted(() => {
  fetchResumes()
})
</script>

<style scoped>
.d-flex.gap-2 > * {
  margin-left: 8px;
}
.d-flex.gap-2 > *:first-child {
  margin-left: 0;
}
</style>
