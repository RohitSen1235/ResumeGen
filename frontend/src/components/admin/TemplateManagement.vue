<template>
  <div class="template-management">
    <!-- Templates Grid -->
    <div class="templates-grid">
      <div v-for="template in templates" :key="template.id" class="template-card">
        <div class="template-preview">
          <img 
            :src="template.image_path || '/template-previews/default.png'" 
            :alt="template.name"
            class="preview-image"
            @error="handleImageError"
          />
        </div>
        <div class="template-info">
          <h3 class="template-name">{{ formatTemplateName(template.name) }}</h3>
          <p class="template-description">{{ template.description || 'Professional resume template' }}</p>
          <div class="template-stats">
            <span class="stat-item">
              <span class="stat-icon">📄</span>
              <span>{{ template.usage || 0 }} uses</span>
            </span>
            <span class="stat-item">
              <span class="stat-icon">⭐</span>
              <span>{{ template.rating || 'N/A' }}</span>
            </span>
          </div>
        </div>
        <div class="template-actions">
          <button @click="previewTemplate(template)" class="action-btn preview">
            👁️ Preview
          </button>
          <button @click="editTemplate(template)" class="action-btn edit">
            ✏️ Edit
          </button>
          <button @click="toggleTemplateStatus(template)" :class="['action-btn', template.is_active ? 'disable' : 'enable']">
            {{ template.is_active ? '🚫 Disable' : '✅ Enable' }}
          </button>
        </div>
      </div>
      
      <!-- Add New Template Card -->
      <div class="template-card add-template" @click="showAddDialog = true">
        <div class="add-template-content">
          <div class="add-icon">➕</div>
          <h3>Add New Template</h3>
          <p>Create a new resume template</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner">Loading templates...</div>
    </div>

    <!-- Empty State -->
    <div v-if="templates.length === 0 && !loading" class="empty-state">
      <div class="empty-icon">📄</div>
      <h3>No Templates Found</h3>
      <p>Start by adding your first resume template</p>
      <button @click="showAddDialog = true" class="btn primary">Add Template</button>
    </div>

    <!-- Add Template Dialog -->
    <div v-if="showAddDialog" class="modal-overlay" @click="showAddDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New Template</h3>
          <button @click="showAddDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Template Name</label>
            <input 
              type="text" 
              v-model="newTemplate.name" 
              placeholder="e.g., Modern Professional"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="newTemplate.description" 
              placeholder="Brief description of the template..."
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>Template File</label>
            <input 
              type="file" 
              @change="handleTemplateFileUpload" 
              accept=".tex,.j2"
              class="form-file"
            />
            <small class="form-help">Upload a LaTeX template file (.tex or .j2)</small>
          </div>
          <div class="form-group">
            <label>Preview Image</label>
            <input 
              type="file" 
              @change="handleImageFileUpload" 
              accept="image/png,image/jpeg"
              class="form-file"
            />
            <small class="form-help">Upload a preview image for the template</small>
          </div>
          <div class="form-group form-group-checkboxes">
            <label class="checkbox-label">
              <input type="checkbox" v-model="newTemplate.is_default" />
              Set as Default
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="newTemplate.single_page" />
              Single Page
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="newTemplate.is_active" />
              Active
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showAddDialog = false" class="btn secondary">Cancel</button>
          <button @click="addTemplate" class="btn primary" :disabled="!canAddTemplate">
            Add Template
          </button>
        </div>
      </div>
    </div>

    <!-- Template Preview Dialog -->
    <div v-if="previewDialog" class="modal-overlay" @click="previewDialog = false">
      <div class="modal-content large" @click.stop>
        <div class="modal-header">
          <h3>Template Preview - {{ formatTemplateName(selectedTemplate?.name || '') }}</h3>
          <button @click="previewDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="preview-container">
            <img 
              :src="selectedTemplate?.image_path || '/template-previews/default.png'" 
              :alt="selectedTemplate?.name"
              class="large-preview"
              @error="handleImageError"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="previewDialog = false" class="btn secondary">Close</button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message.show" :class="['message', message.type]">
      {{ message.text }}
    </div>

    <!-- Edit Template Dialog -->
    <div v-if="showEditDialog" class="modal-overlay" @click="showEditDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit Template</h3>
          <button @click="showEditDialog = false" class="close-btn">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Template Name</label>
            <input type="text" v-model="editableTemplate.name" class="form-input" />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editableTemplate.description" class="form-textarea" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Template File (Optional)</label>
            <input type="file" @change="handleEditTemplateFileUpload" accept=".tex,.j2" class="form-file" />
            <small class="form-help">Upload a new LaTeX file to replace the existing one.</small>
          </div>
          <div class="form-group">
            <label>Preview Image (Optional)</label>
            <input type="file" @change="handleEditImageFileUpload" accept="image/png,image/jpeg" class="form-file" />
            <small class="form-help">Upload a new preview image to replace the existing one.</small>
          </div>
          <div class="form-group form-group-checkboxes">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editableTemplate.is_default" />
              Set as Default
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="editableTemplate.single_page" />
              Single Page
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="editableTemplate.is_active" />
              Active
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showEditDialog = false" class="btn secondary">Cancel</button>
          <button @click="updateTemplate" class="btn primary">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost/api'
})

interface Template {
  id: string
  name: string
  description?: string
  file_path: string
  image_path?: string
  is_default: boolean
  single_page: boolean
  is_active: boolean
  usage?: number
  rating?: string
  template_file?: File
  image_file?: File
}

export default defineComponent({
  name: 'TemplateManagement',
  setup() {
    const auth = useAuthStore()
    const templates = ref<Template[]>([])
    const loading = ref(false)
    const showAddDialog = ref(false)
    const showEditDialog = ref(false)
    const previewDialog = ref(false)
    const selectedTemplate = ref<Template | null>(null)
    const editableTemplate = ref<Partial<Template>>({})

    const newTemplate = ref({
      name: '',
      description: '',
      template_file: null as File | null,
      image_file: null as File | null,
      is_default: false,
      single_page: true,
      is_active: true
    })

    const message = ref({
      show: false,
      text: '',
      type: 'success'
    })

    const canAddTemplate = computed(() => {
      return newTemplate.value.name.trim() && newTemplate.value.template_file && newTemplate.value.image_file
    })

    const showMessage = (text: string, type: 'success' | 'error' = 'success') => {
      message.value = { show: true, text, type }
      setTimeout(() => {
        message.value.show = false
      }, 3000)
    }

    const formatTemplateName = (name: string) => {
      return name.replace(/template_|_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    }

    const fetchTemplates = async () => {
      try {
        loading.value = true
        const response = await apiClient.get('/admin/templates', {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        
        // Transform the response to match our interface
        templates.value = response.data.map((template: any) => ({
          ...template,
          usage: Math.floor(Math.random() * 100), // Mock usage data
          rating: (4 + Math.random()).toFixed(1) // Mock rating data
        }))
        
      } catch (error) {
        console.error('Error fetching templates:', error)
        showMessage('Error fetching templates', 'error')
      } finally {
        loading.value = false
      }
    }

    const handleImageError = (event: Event) => {
      const img = event.target as HTMLImageElement
      img.src = '/template-previews/default.png' // Fallback image
    }

    const previewTemplate = (template: Template) => {
      selectedTemplate.value = template
      previewDialog.value = true
    }

    const editTemplate = (template: Template) => {
      editableTemplate.value = { ...template }
      showEditDialog.value = true
    }

    const handleEditTemplateFileUpload = (event: Event) => {
      const target = event.target as HTMLInputElement
      if (target.files && target.files[0]) {
        editableTemplate.value.template_file = target.files[0]
      }
    }

    const handleEditImageFileUpload = (event: Event) => {
      const target = event.target as HTMLInputElement
      if (target.files && target.files[0]) {
        editableTemplate.value.image_file = target.files[0]
      }
    }

    const updateTemplate = async () => {
      if (!editableTemplate.value.id) return

      try {
        const formData = new FormData()
        formData.append('name', editableTemplate.value.name || '')
        formData.append('description', editableTemplate.value.description || '')
        
        if (editableTemplate.value.template_file) {
          formData.append('template_file', editableTemplate.value.template_file)
        }
        if (editableTemplate.value.image_file) {
          formData.append('image_file', editableTemplate.value.image_file)
        }

        await apiClient.put(`/admin/templates/${editableTemplate.value.id}`, formData, {
          headers: {
            Authorization: `Bearer ${auth.token}`,
            'Content-Type': 'multipart/form-data'
          }
        })

        showEditDialog.value = false
        await fetchTemplates()
        showMessage('Template updated successfully')
      } catch (error) {
        console.error('Error updating template:', error)
        showMessage('Error updating template', 'error')
      }
    }

    const deleteTemplate = async (templateId: string) => {
      if (!confirm('Are you sure you want to delete this template?')) {
        return
      }
      try {
        await apiClient.delete(`/admin/templates/${templateId}`, {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        await fetchTemplates()
        showMessage('Template deleted successfully')
      } catch (error) {
        console.error('Error deleting template:', error)
        showMessage('Error deleting template', 'error')
      }
    }

    const toggleTemplateStatus = async (template: Template) => {
      try {
        const updatedStatus = !template.is_active
        await apiClient.put(`/admin/templates/${template.id}`, { is_active: updatedStatus }, {
          headers: {
            Authorization: `Bearer ${auth.token}`
          }
        })
        template.is_active = updatedStatus
        showMessage(`Template ${template.is_active ? 'enabled' : 'disabled'}`)
      } catch (error) {
        showMessage('Error updating template status', 'error')
      }
    }

    const handleTemplateFileUpload = (event: Event) => {
      const target = event.target as HTMLInputElement
      if (target.files && target.files[0]) {
        newTemplate.value.template_file = target.files[0]
      }
    }

    const handleImageFileUpload = (event: Event) => {
      const target = event.target as HTMLInputElement
      if (target.files && target.files[0]) {
        newTemplate.value.image_file = target.files[0]
      }
    }

    const addTemplate = async () => {
      try {
        const formData = new FormData()
        formData.append('name', newTemplate.value.name)
        formData.append('description', newTemplate.value.description)
        formData.append('is_default', String(newTemplate.value.is_default))
        formData.append('single_page', String(newTemplate.value.single_page))
        formData.append('is_active', String(newTemplate.value.is_active))
        if (newTemplate.value.template_file) {
          formData.append('template_file', newTemplate.value.template_file)
        }
        if (newTemplate.value.image_file) {
          formData.append('image_file', newTemplate.value.image_file)
        }

        await apiClient.post('/admin/templates', formData, {
          headers: {
            Authorization: `Bearer ${auth.token}`,
            'Content-Type': 'multipart/form-data'
          }
        })

        showAddDialog.value = false
        newTemplate.value = { name: '', description: '', template_file: null, image_file: null, is_default: false, single_page: true, is_active: true }
        await fetchTemplates()
        showMessage('Template added successfully')
      } catch (error) {
        console.error('Error adding template:', error)
        showMessage('Error adding template', 'error')
      }
    }

    onMounted(fetchTemplates)

    return {
      auth,
      templates,
      loading,
      showAddDialog,
      previewDialog,
      selectedTemplate,
      newTemplate,
      message,
      canAddTemplate,
      formatTemplateName,
      fetchTemplates,
      handleImageError,
      previewTemplate,
      editTemplate,
      deleteTemplate,
      toggleTemplateStatus,
      handleTemplateFileUpload,
      handleImageFileUpload,
      addTemplate,
      showEditDialog,
      editableTemplate,
      handleEditTemplateFileUpload,
      handleEditImageFileUpload,
      updateTemplate
    }
  }
})
</script>

<style scoped>
.template-management {
  width: 100%;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.template-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.template-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
}

.template-preview {
  height: 200px;
  overflow: hidden;
  background: #f8f9fa;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.template-info {
  padding: 1rem;
}

.template-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.template-description {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.template-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #7f8c8d;
}

.stat-icon {
  font-size: 0.9rem;
}

.template-actions {
  padding: 0 1rem 1rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.action-btn {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 80px;
}

.action-btn.preview {
  background: #3498db;
  color: white;
}

.action-btn.preview:hover {
  background: #2980b9;
}

.action-btn.edit {
  background: #f39c12;
  color: white;
}

.action-btn.edit:hover {
  background: #e67e22;
}

.action-btn.enable {
  background: #27ae60;
  color: white;
}

.action-btn.enable:hover {
  background: #229954;
}

.action-btn.disable {
  background: #e74c3c;
  color: white;
}

.action-btn.disable:hover {
  background: #c0392b;
}

.add-template {
  border: 2px dashed #bdc3c7;
  background: #f8f9fa;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.add-template:hover {
  border-color: #3498db;
  background: #ecf0f1;
}

.add-template-content {
  text-align: center;
  color: #7f8c8d;
}

.add-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.add-template-content h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.add-template-content p {
  margin: 0;
  font-size: 0.9rem;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
}

.loading-spinner {
  font-size: 1.1rem;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.empty-state h3 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-content.large {
  max-width: 800px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group-checkboxes {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.form-group label {
  display: block;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
}

.form-file {
  width: 100%;
  padding: 0.5rem;
  border: 2px dashed #e9ecef;
  border-radius: 8px;
  background: #f8f9fa;
  cursor: pointer;
}

.form-help {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.8rem;
  color: #7f8c8d;
}

.preview-container {
  text-align: center;
}

.large-preview {
  max-width: 100%;
  max-height: 600px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn.primary {
  background: #3498db;
  color: white;
}

.btn.primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn.secondary {
  background: #95a5a6;
  color: white;
}

.btn.secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  z-index: 1001;
  animation: slideIn 0.3s ease;
}

.message.success {
  background: #27ae60;
}

.message.error {
  background: #e74c3c;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .template-actions {
    flex-direction: column;
  }
  
  .action-btn {
    flex: none;
  }
  
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 1rem;
  }
}
</style>
