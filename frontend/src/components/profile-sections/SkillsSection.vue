<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <div class="text-h6">Skills</div>
      <v-btn color="primary" variant="flat" @click="showAddDialog = true" prepend-icon="mdi-plus">
        Add Skill
      </v-btn>
    </div>

    <div v-if="skills.length === 0" class="text-center py-8">
      <v-icon icon="mdi-star-outline" size="64" color="grey-lighten-1"></v-icon>
      <div class="text-h6 text-grey-lighten-1 mt-4">No skills added yet</div>
      <div class="text-body-2 text-grey-lighten-1">Add your technical and soft skills</div>
    </div>

    <div v-else>
      <!-- Group skills by category -->
      <div v-for="(categorySkills, category) in groupedSkills" :key="category" class="mb-6">
        <div class="text-subtitle-1 font-weight-bold mb-3">{{ category || 'Other' }}</div>
        <v-row>
          <v-col v-for="skill in categorySkills" :key="skill.id" cols="12" sm="6" md="4">
            <v-card variant="outlined" class="pa-3" rounded="lg">
              <div class="d-flex justify-space-between align-center">
                <div class="flex-grow-1">
                  <div class="font-weight-bold">{{ skill.name }}</div>
                  <div v-if="skill.proficiency" class="text-caption text-primary">{{ skill.proficiency }}</div>
                  <div v-if="skill.years_experience" class="text-caption text-grey-darken-1">
                    {{ skill.years_experience }} years
                  </div>
                </div>
                <v-menu>
                  <template v-slot:activator="{ props }">
                    <v-btn icon="mdi-dots-vertical" variant="text" size="small" v-bind="props"></v-btn>
                  </template>
                  <v-list>
                    <v-list-item @click="editSkill(skill)">
                      <v-list-item-title>
                        <v-icon icon="mdi-pencil" class="mr-2"></v-icon>
                        Edit
                      </v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="deleteSkill(skill.id)">
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
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="showAddDialog" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5">
          {{ editingSkill ? 'Edit' : 'Add' }} Skill
        </v-card-title>
        <v-card-text>
          <v-form v-model="formValid">
            <v-text-field
              v-model="formData.name"
              label="Skill Name *"
              :rules="[v => !!v || 'Skill name is required']"
              variant="outlined"
              density="comfortable"
            ></v-text-field>

            <v-text-field
              v-model="formData.category"
              label="Category"
              variant="outlined"
              density="comfortable"
              placeholder="e.g., Programming, Languages, Tools"
            ></v-text-field>

            <v-select
              v-model="formData.proficiency"
              label="Proficiency Level"
              :items="['Beginner', 'Intermediate', 'Advanced', 'Expert']"
              variant="outlined"
              density="comfortable"
              clearable
            ></v-select>

            <v-text-field
              v-model="formData.years_experience"
              label="Years of Experience"
              type="number"
              variant="outlined"
              density="comfortable"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="closeDialog">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="saveSkill" :disabled="!formValid">
            {{ editingSkill ? 'Update' : 'Add' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Skill {
  id: string
  name: string
  category?: string
  proficiency?: 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert'
  years_experience?: number
}

const props = defineProps<{
  skills: Skill[]
}>()

const emit = defineEmits<{
  add: [skill: Omit<Skill, 'id'>]
  edit: [id: string, skill: Omit<Skill, 'id'>]
  delete: [id: string]
}>()

const showAddDialog = ref(false)
const editingSkill = ref<Skill | null>(null)
const formValid = ref(false)

const formData = ref({
  name: '',
  category: '',
  proficiency: null as string | null,
  years_experience: null as number | null,
})

const groupedSkills = computed(() => {
  const groups: Record<string, Skill[]> = {}
  props.skills.forEach(skill => {
    const category = skill.category || 'Other'
    if (!groups[category]) {
      groups[category] = []
    }
    groups[category].push(skill)
  })
  return groups
})

const editSkill = (skill: Skill) => {
  editingSkill.value = skill
  formData.value = {
    name: skill.name,
    category: skill.category || '',
    proficiency: skill.proficiency || null,
    years_experience: skill.years_experience || null,
  }
  showAddDialog.value = true
}

const deleteSkill = (id: string) => {
  emit('delete', id)
}

const saveSkill = () => {
  const skillData = {
    ...formData.value,
    proficiency: formData.value.proficiency as 'Beginner' | 'Intermediate' | 'Advanced' | 'Expert' | undefined,
    years_experience: formData.value.years_experience || undefined,
  }

  if (editingSkill.value) {
    emit('edit', editingSkill.value.id, skillData)
  } else {
    emit('add', skillData)
  }

  closeDialog()
}

const closeDialog = () => {
  showAddDialog.value = false
  editingSkill.value = null
  formData.value = {
    name: '',
    category: '',
    proficiency: null,
    years_experience: null,
  }
}
</script>
