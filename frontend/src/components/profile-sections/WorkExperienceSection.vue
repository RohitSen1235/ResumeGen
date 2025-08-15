<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <div class="text-h6">Work Experience</div>
      <v-btn color="primary" variant="flat" @click="showAddDialog = true" prepend-icon="mdi-plus">
        Add Experience
      </v-btn>
    </div>

    <div v-if="experiences.length === 0" class="text-center py-8">
      <v-icon icon="mdi-briefcase-outline" size="64" color="grey-lighten-1"></v-icon>
      <div class="text-h6 text-grey-lighten-1 mt-4">No work experience added yet</div>
      <div class="text-body-2 text-grey-lighten-1">Add your work experience to showcase your professional background</div>
    </div>

    <v-row v-else>
      <v-col v-for="experience in experiences" :key="experience.id" cols="12" md="6">
        <v-card variant="outlined" class="pa-4" rounded="lg">
          <div class="d-flex justify-space-between align-start mb-2">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold">{{ experience.position }}</div>
              <div class="text-subtitle-1 text-primary">{{ experience.company }}</div>
              <div class="text-caption text-grey-darken-1">
                {{ formatDate(experience.start_date) }} - 
                {{ experience.current_job ? 'Present' : formatDate(experience.end_date) }}
              </div>
              <div v-if="experience.location" class="text-caption text-grey-darken-1">
                <v-icon icon="mdi-map-marker" size="small" class="mr-1"></v-icon>
                {{ experience.location }}
              </div>
            </div>
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon="mdi-dots-vertical" variant="text" size="small" v-bind="props"></v-btn>
              </template>
              <v-list>
                <v-list-item @click="editExperience(experience)">
                  <v-list-item-title>
                    <v-icon icon="mdi-pencil" class="mr-2"></v-icon>
                    Edit
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="deleteExperience(experience.id)">
                  <v-list-item-title class="text-error">
                    <v-icon icon="mdi-delete" class="mr-2"></v-icon>
                    Delete
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
          
          <div v-if="experience.description" class="text-body-2 mb-2">
            {{ experience.description }}
          </div>
          
          <div v-if="experience.achievements?.length" class="mb-2">
            <div class="text-caption font-weight-bold mb-1">Key Achievements:</div>
            <ul class="text-body-2">
              <li v-for="achievement in experience.achievements" :key="achievement">
                {{ achievement }}
              </li>
            </ul>
          </div>
          
          <div v-if="experience.technologies?.length">
            <div class="text-caption font-weight-bold mb-1">Technologies:</div>
            <v-chip-group>
              <v-chip v-for="tech in experience.technologies" :key="tech" size="small" variant="outlined">
                {{ tech }}
              </v-chip>
            </v-chip-group>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showAddDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h5">
          {{ editingExperience ? 'Edit' : 'Add' }} Work Experience
        </v-card-title>
        <v-card-text>
          <v-form v-model="formValid">
            <v-text-field
              v-model="formData.position"
              label="Position *"
              :rules="[v => !!v || 'Position is required']"
              variant="outlined"
              density="comfortable"
            ></v-text-field>

            <v-text-field
              v-model="formData.company"
              label="Company *"
              :rules="[v => !!v || 'Company is required']"
              variant="outlined"
              density="comfortable"
            ></v-text-field>

            <v-text-field
              v-model="formData.location"
              label="Location"
              variant="outlined"
              density="comfortable"
              placeholder="Optional"
            ></v-text-field>

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
                  :disabled="formData.current_job"
                ></v-text-field>
              </v-col>
            </v-row>

            <v-checkbox
              v-model="formData.current_job"
              label="I currently work here"
              color="primary"
            ></v-checkbox>

            <v-textarea
              v-model="formData.description"
              label="Job Description"
              variant="outlined"
              density="comfortable"
              rows="3"
              placeholder="Describe your role and responsibilities"
            ></v-textarea>

            <v-textarea
              v-model="achievementsText"
              label="Key Achievements (one per line)"
              variant="outlined"
              density="comfortable"
              rows="3"
              placeholder="• Increased sales by 25%&#10;• Led a team of 5 developers&#10;• Implemented new processes"
            ></v-textarea>

            <v-textarea
              v-model="technologiesText"
              label="Technologies (comma separated)"
              variant="outlined"
              density="comfortable"
              rows="2"
              placeholder="JavaScript, React, Node.js, Python"
            ></v-textarea>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="closeDialog">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveExperience" :disabled="!formValid">
            {{ editingExperience ? 'Update' : 'Add' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface WorkExperience {
  id: string
  position: string
  company: string
  location?: string
  start_date?: string
  end_date?: string
  current_job: boolean
  description?: string
  achievements?: string[]
  technologies?: string[]
}

const props = defineProps<{
  experiences: WorkExperience[]
}>()

const emit = defineEmits<{
  add: [experience: Omit<WorkExperience, 'id'>]
  edit: [id: string, experience: Omit<WorkExperience, 'id'>]
  delete: [id: string]
}>()

const showAddDialog = ref(false)
const editingExperience = ref<WorkExperience | null>(null)
const formValid = ref(false)

const formData = ref({
  position: '',
  company: '',
  location: '',
  start_date: '',
  end_date: '',
  current_job: false,
  description: '',
})

const achievementsText = ref('')
const technologiesText = ref('')

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short' 
  })
}

const editExperience = (experience: WorkExperience) => {
  editingExperience.value = experience
  formData.value = {
    position: experience.position,
    company: experience.company,
    location: experience.location || '',
    start_date: experience.start_date || '',
    end_date: experience.end_date || '',
    current_job: experience.current_job,
    description: experience.description || '',
  }
  achievementsText.value = experience.achievements?.join('\n') || ''
  technologiesText.value = experience.technologies?.join(', ') || ''
  showAddDialog.value = true
}

const deleteExperience = (id: string) => {
  emit('delete', id)
}

const saveExperience = () => {
  const achievements = achievementsText.value
    .split('\n')
    .map(line => line.trim().replace(/^[•\-\*]\s*/, ''))
    .filter(line => line.length > 0)

  const technologies = technologiesText.value
    .split(',')
    .map(tech => tech.trim())
    .filter(tech => tech.length > 0)

  const experienceData = {
    ...formData.value,
    achievements: achievements.length > 0 ? achievements : undefined,
    technologies: technologies.length > 0 ? technologies : undefined,
  }

  if (editingExperience.value) {
    emit('edit', editingExperience.value.id, experienceData)
  } else {
    emit('add', experienceData)
  }

  closeDialog()
}

const closeDialog = () => {
  showAddDialog.value = false
  editingExperience.value = null
  formData.value = {
    position: '',
    company: '',
    location: '',
    start_date: '',
    end_date: '',
    current_job: false,
    description: '',
  }
  achievementsText.value = ''
  technologiesText.value = ''
}
</script>
