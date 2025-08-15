<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <div class="text-h6">Education</div>
      <v-btn color="primary" variant="flat" @click="showAddDialog = true" prepend-icon="mdi-plus">
        Add Education
      </v-btn>
    </div>

    <div v-if="educations.length === 0" class="text-center py-8">
      <v-icon icon="mdi-school-outline" size="64" color="grey-lighten-1"></v-icon>
      <div class="text-h6 text-grey-lighten-1 mt-4">No education added yet</div>
      <div class="text-body-2 text-grey-lighten-1">Add your educational background</div>
    </div>

    <v-row v-else>
      <v-col v-for="education in educations" :key="education.id" cols="12" md="6">
        <v-card variant="outlined" class="pa-4" rounded="lg">
          <div class="d-flex justify-space-between align-start mb-2">
            <div class="flex-grow-1">
              <div class="text-h6 font-weight-bold">{{ education.degree }}</div>
              <div class="text-subtitle-1 text-primary">{{ education.institution }}</div>
              <div v-if="education.field_of_study" class="text-body-2">{{ education.field_of_study }}</div>
              <div class="text-caption text-grey-darken-1">
                {{ formatDate(education.start_date) }} - {{ formatDate(education.end_date) }}
              </div>
              <div v-if="education.gpa" class="text-caption">GPA: {{ education.gpa }}</div>
            </div>
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn icon="mdi-dots-vertical" variant="text" size="small" v-bind="props"></v-btn>
              </template>
              <v-list>
                <v-list-item @click="editEducation(education)">
                  <v-list-item-title>
                    <v-icon icon="mdi-pencil" class="mr-2"></v-icon>
                    Edit
                  </v-list-item-title>
                </v-list-item>
                <v-list-item @click="deleteEducation(education.id)">
                  <v-list-item-title class="text-error">
                    <v-icon icon="mdi-delete" class="mr-2"></v-icon>
                    Delete
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showAddDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h5">
          {{ editingEducation ? 'Edit' : 'Add' }} Education
        </v-card-title>
        <v-card-text>
          <v-form v-model="formValid">
            <v-text-field
              v-model="formData.institution"
              label="Institution *"
              :rules="[v => !!v || 'Institution is required']"
              variant="outlined"
              density="comfortable"
            ></v-text-field>

            <v-text-field
              v-model="formData.degree"
              label="Degree *"
              :rules="[v => !!v || 'Degree is required']"
              variant="outlined"
              density="comfortable"
            ></v-text-field>

            <v-text-field
              v-model="formData.field_of_study"
              label="Field of Study"
              variant="outlined"
              density="comfortable"
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
                ></v-text-field>
              </v-col>
            </v-row>

            <v-text-field
              v-model="formData.gpa"
              label="GPA"
              type="number"
              step="0.01"
              variant="outlined"
              density="comfortable"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="closeDialog">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveEducation" :disabled="!formValid">
            {{ editingEducation ? 'Update' : 'Add' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Education {
  id: string
  institution: string
  degree: string
  field_of_study?: string
  location?: string
  start_date?: string
  end_date?: string
  gpa?: number
}

const props = defineProps<{
  educations: Education[]
}>()

const emit = defineEmits<{
  add: [education: Omit<Education, 'id'>]
  edit: [id: string, education: Omit<Education, 'id'>]
  delete: [id: string]
}>()

const showAddDialog = ref(false)
const editingEducation = ref<Education | null>(null)
const formValid = ref(false)

const formData = ref({
  institution: '',
  degree: '',
  field_of_study: '',
  start_date: '',
  end_date: '',
  gpa: null as number | null,
})

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short' 
  })
}

const editEducation = (education: Education) => {
  editingEducation.value = education
  formData.value = {
    institution: education.institution,
    degree: education.degree,
    field_of_study: education.field_of_study || '',
    start_date: education.start_date || '',
    end_date: education.end_date || '',
    gpa: education.gpa || null,
  }
  showAddDialog.value = true
}

const deleteEducation = (id: string) => {
  emit('delete', id)
}

const saveEducation = () => {
  const educationData = {
    ...formData.value,
    gpa: formData.value.gpa || undefined,
  }

  if (editingEducation.value) {
    emit('edit', editingEducation.value.id, educationData)
  } else {
    emit('add', educationData)
  }

  closeDialog()
}

const closeDialog = () => {
  showAddDialog.value = false
  editingEducation.value = null
  formData.value = {
    institution: '',
    degree: '',
    field_of_study: '',
    start_date: '',
    end_date: '',
    gpa: null,
  }
}
</script>
