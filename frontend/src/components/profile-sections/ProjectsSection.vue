<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <div class="text-h6">Projects</div>
      <v-btn color="primary" variant="flat" @click="showAddDialog = true" prepend-icon="mdi-plus">
        Add Project
      </v-btn>
    </div>

    <div v-if="projects.length === 0" class="text-center py-8">
      <v-icon icon="mdi-code-tags" size="64" color="grey-lighten-1"></v-icon>
      <div class="text-h6 text-grey-lighten-1 mt-4">No projects added yet</div>
      <div class="text-body-2 text-grey-lighten-1">Showcase your personal and professional projects</div>
    </div>

    <v-row v-else>
      <v-col v-for="project in projects" :key="project.id" cols="12" md="6">
        <v-card variant="outlined" class="pa-4" rounded="lg">
          <div class="d-flex justify-space-between align-start mb-2">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold">{{ project.name }}</div>
              <div class="text-caption text-grey-darken-1 mb-2">
                {{ formatDate(project.start_date) }} - {{ formatDate(project.end_date) || 'Ongoing' }}
              </div>
              <div v-if="project.description" class="text-body-2 mb-3">
                {{ project.description }}
              </div>
              <div v-if="project.url" class="mb-2">
                <v-btn :href="project.url" target="_blank" variant="text" size="small" prepend-icon="mdi-web">
                  Live Demo
                </v-btn>
              </div>
              <div v-if="project.industry" class="text-caption text-grey-darken-1">
                <v-icon icon="mdi-factory" size="small" class="mr-1"></v-icon>
                {{ project.industry }}
              </div>
            </div>
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon="mdi-dots-vertical" variant="text" size="small" v-bind="props"></v-btn>
              </template>
              <v-list>
                <v-list-item @click="editProject(project)">
                  <v-list-item-title>
                    <v-icon icon="mdi-pencil" class="mr-2"></v-icon>
                    Edit
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="deleteProject(project.id)">
                  <v-list-item-title class="text-error">
                    <v-icon icon="mdi-delete" class="mr-2"></v-icon>
                    Delete
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
          
          <div v-if="project.technologies?.length" class="mb-2">
            <div class="text-caption font-weight-bold mb-1">Technologies:</div>
            <v-chip-group>
              <v-chip v-for="tech in project.technologies" :key="tech" size="small" variant="outlined">
                {{ tech }}
              </v-chip>
            </v-chip-group>
          </div>
          
          <div v-if="project.achievements?.length">
            <div class="text-caption font-weight-bold mb-1">Key Achievements:</div>
            <ul class="text-body-2">
              <li v-for="achievement in project.achievements" :key="achievement">
                {{ achievement }}
              </li>
            </ul>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showAddDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h5">
          {{ editingProject ? 'Edit' : 'Add' }} Project
        </v-card-title>
        <v-card-text>
          <v-form v-model="formValid">
            <v-text-field
              v-model="formData.name"
              label="Project Name *"
              :rules="[v => !!v || 'Project name is required']"
              variant="outlined"
              density="comfortable"
            ></v-text-field>

            <v-textarea
              v-model="formData.description"
              label="Project Description"
              variant="outlined"
              density="comfortable"
              rows="3"
              placeholder="Describe what the project does and your role"
            ></v-textarea>

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="formData.url"
                  label="Live Demo URL"
                  variant="outlined"
                  density="comfortable"
                  placeholder="https://..."
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="formData.industry"
                  label="Industry"
                  variant="outlined"
                  density="comfortable"
                  placeholder="e.g., SaaS, E-commerce"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="formData.start_date"
                  label="Start Date"
                  type="date"
                  variant="outlined"
                  density="comfortable"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model="formData.end_date"
                  label="End Date"
                  type="date"
                  variant="outlined"
                  density="comfortable"
                  placeholder="Leave empty if ongoing"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-textarea
              v-model="technologiesText"
              label="Technologies (comma separated)"
              variant="outlined"
              density="comfortable"
              rows="2"
              placeholder="React, Node.js, MongoDB, AWS"
            ></v-textarea>

            <v-textarea
              v-model="achievementsText"
              label="Key Achievements (one per line)"
              variant="outlined"
              density="comfortable"
              rows="3"
              placeholder="• Achieved 99% uptime&#10;• Reduced load time by 50%&#10;• Gained 1000+ users"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="closeDialog">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveProject" :disabled="!formValid">
            {{ editingProject ? 'Update' : 'Add' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Project {
  id: string
  name: string
  description?: string
  url?: string
  industry?: string
  start_date?: string
  end_date?: string
  technologies?: string[]
  achievements?: string[]
}

const props = defineProps<{
  projects: Project[]
}>()

const emit = defineEmits<{
  add: [project: Omit<Project, 'id'>]
  edit: [id: string, project: Omit<Project, 'id'>]
  delete: [id: string]
}>()

const showAddDialog = ref(false)
const editingProject = ref<Project | null>(null)
const formValid = ref(false)

const formData = ref({
  name: '',
  description: '',
  url: '',
  industry: '',
  start_date: '',
  end_date: '',
})

const technologiesText = ref('')
const achievementsText = ref('')

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short' 
  })
}

const editProject = (project: Project) => {
  editingProject.value = project
  formData.value = {
    name: project.name,
    description: project.description || '',
    url: project.url || '',
    industry: project.industry || '',
    start_date: project.start_date || '',
    end_date: project.end_date || '',
  }
  technologiesText.value = project.technologies?.join(', ') || ''
  achievementsText.value = project.achievements?.join('\n') || ''
  showAddDialog.value = true
}

const deleteProject = (id: string) => {
  emit('delete', id)
}

const saveProject = () => {
  const technologies = technologiesText.value
    .split(',')
    .map(tech => tech.trim())
    .filter(tech => tech.length > 0)

  const achievements = achievementsText.value
    .split('\n')
    .map(line => line.trim().replace(/^[•\-\*]\s*/, ''))
    .filter(line => line.length > 0)

  const projectData = {
    ...formData.value,
    technologies: technologies.length > 0 ? technologies : undefined,
    achievements: achievements.length > 0 ? achievements : undefined,
  }

  if (editingProject.value) {
    emit('edit', editingProject.value.id, projectData)
  } else {
    emit('add', projectData)
  }

  closeDialog()
}

const closeDialog = () => {
  showAddDialog.value = false
  editingProject.value = null
  formData.value = {
    name: '',
    description: '',
    url: '',
    industry: '',
    start_date: '',
    end_date: '',
  }
  technologiesText.value = ''
  achievementsText.value = ''
}
</script>
