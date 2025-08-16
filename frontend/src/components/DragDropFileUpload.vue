<template>
  <div
    ref="dropZone"
    class="drag-drop-zone"
    :class="{
      'drag-over': isDragOver,
      'has-file': !!modelValue,
      'error': hasError
    }"
    @click="triggerFileInput"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
  >
    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <div class="mt-4">Processing your resume...</div>
    </div>

    <!-- Hidden file input -->
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      @change="handleFileSelect"
      style="display: none"
    />

    <!-- Upload State -->
    <div v-if="!modelValue" class="upload-content">
      <div class="upload-icon-container">
        <v-icon
          :icon="isDragOver ? 'mdi-cloud-upload' : 'mdi-cloud-upload-outline'"
          :size="isDragOver ? 80 : 64"
          :color="isDragOver ? 'primary' : 'grey-darken-1'"
          class="upload-icon"
        ></v-icon>
      </div>
      
      <div class="upload-text">
        <h3 class="text-h6 font-weight-medium mb-2" :class="isDragOver ? 'text-primary' : 'text-grey-darken-2'">
          {{ isDragOver ? 'Drop your file here' : title }}
        </h3>
        <p class="text-body-2 text-grey-darken-1 mb-3">
          {{ isDragOver ? 'Release to upload' : 'Drag and drop your file here, or click to browse' }}
        </p>
        <v-chip
          variant="outlined"
          color="primary"
          size="small"
          class="mb-2"
        >
          Supported: {{ supportedFormats }}
        </v-chip>
      </div>

      <v-btn
        v-if="!isDragOver"
        color="primary"
        variant="outlined"
        prepend-icon="mdi-folder-open-outline"
        class="mt-4"
        @click.stop="triggerFileInput"
      >
        Browse Files
      </v-btn>
    </div>

    <!-- File Selected State -->
    <div v-else class="file-selected-content">
      <div class="file-info">
        <v-icon
          :icon="getFileIcon(modelValue)"
          size="48"
          color="success"
          class="mb-3"
        ></v-icon>
        
        <h4 class="text-h6 font-weight-medium mb-1">{{ modelValue.name }}</h4>
        <p class="text-body-2 text-grey-darken-1 mb-2">{{ formatFileSize(modelValue.size) }}</p>
        
        <v-chip
          color="success"
          variant="tonal"
          size="small"
          prepend-icon="mdi-check-circle"
          class="mb-4"
        >
          File Ready
        </v-chip>
      </div>

      <div class="file-actions">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-swap-horizontal"
          size="small"
          @click.stop="triggerFileInput"
          class="mr-2"
        >
          Change File
        </v-btn>
        <v-btn
          color="error"
          variant="text"
          icon="mdi-close"
          size="small"
          @click.stop="removeFile"
        ></v-btn>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="hasError" class="error-message mt-3">
      <v-alert
        type="error"
        variant="tonal"
        density="compact"
        :text="errorMessage"
      ></v-alert>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  modelValue?: File | null
  accept?: string
  maxSize?: number // in MB
  loading?: boolean
  errorMessage?: string
  title?: string
  supportedFormats?: string
}

interface Emits {
  (e: 'update:modelValue', file: File | null): void
  (e: 'error', message: string): void
  (e: 'file-selected', file: File): void
}

const props = withDefaults(defineProps<Props>(), {
  accept: '.txt,.pdf,.doc,.docx',
  maxSize: 10, // 10MB default
  loading: false,
  errorMessage: '',
  title: 'Upload Job Description',
  supportedFormats: 'TXT'
})

const emit = defineEmits<Emits>()

const dropZone = ref<HTMLElement>()
const fileInput = ref<HTMLInputElement>()
const isDragOver = ref(false)

const hasError = computed(() => !!props.errorMessage)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  // Only set to false if we're leaving the drop zone entirely
  if (!dropZone.value?.contains(e.relatedTarget as Node)) {
    isDragOver.value = false
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

const handleFile = (file: File) => {
  // Validate file type
  const acceptedTypes = props.accept.split(',').map(type => type.trim())
  const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
  
  if (!acceptedTypes.includes(fileExtension)) {
    emit('error', `File type not supported. Please upload: ${props.accept}`)
    return
  }

  // Validate file size
  const fileSizeMB = file.size / (1024 * 1024)
  if (fileSizeMB > props.maxSize) {
    emit('error', `File size too large. Maximum size: ${props.maxSize}MB`)
    return
  }

  // Clear any previous errors
  emit('error', '')
  
  // Emit the file
  emit('update:modelValue', file)
  emit('file-selected', file)
}

const removeFile = () => {
  emit('update:modelValue', null)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const getFileIcon = (file: File): string => {
  const extension = file.name.split('.').pop()?.toLowerCase()
  switch (extension) {
    case 'pdf':
      return 'mdi-file-pdf-box'
    case 'doc':
    case 'docx':
      return 'mdi-file-word-box'
    case 'txt':
      return 'mdi-file-document-outline'
    default:
      return 'mdi-file-outline'
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.drag-drop-zone {
  border: 2px dashed #e0e0e0;
  border-radius: 16px;
  padding: 32px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  position: relative;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.drag-drop-zone:hover {
  border-color: #2196f3;
  background: linear-gradient(135deg, #f3f9ff 0%, #e8f4fd 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.15);
}

.drag-drop-zone.drag-over {
  border-color: #2196f3;
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  transform: scale(1.02);
  box-shadow: 0 12px 35px rgba(33, 150, 243, 0.25);
}

.drag-drop-zone.has-file {
  border-color: #4caf50;
  background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e8 100%);
}

.drag-drop-zone.error {
  border-color: #f44336;
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.upload-icon-container {
  margin-bottom: 16px;
}

.upload-icon {
  transition: all 0.3s ease;
}

.upload-text {
  margin-bottom: 16px;
}

.file-selected-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.file-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 16px;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-message {
  width: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  backdrop-filter: blur(4px);
}

/* Mobile responsiveness */
@media (max-width: 600px) {
  .drag-drop-zone {
    padding: 24px 16px;
    min-height: 160px;
  }
  
  .upload-icon {
    font-size: 48px !important;
  }
  
  .upload-text h3 {
    font-size: 1.1rem;
  }
  
  .upload-text p {
    font-size: 0.875rem;
  }
}

/* Animation for file icon */
@keyframes fileSuccess {
  0% {
    transform: scale(0.8);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.file-selected-content .v-icon {
  animation: fileSuccess 0.5s ease-out;
}

/* Pulse animation for drag over state */
@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(33, 150, 243, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(33, 150, 243, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(33, 150, 243, 0);
  }
}

.drag-drop-zone.drag-over {
  animation: pulse 1.5s infinite;
}
</style>
