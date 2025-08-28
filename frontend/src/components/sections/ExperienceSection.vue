<template>
  <div class="experience-section" :style="containerStyles">
    <!-- Section Title -->
    <h2 
      class="section-title"
      :style="definition.styling?.section_title"
    >
      {{ sectionName }}
    </h2>

    <!-- Experience Items -->
    <div class="experience-items">
      <div
        v-for="(experience, index) in experienceList"
        :key="index"
        class="experience-item"
        :style="definition.styling?.item_container"
      >
        <!-- Experience Header -->
        <div class="experience-header" :style="definition.styling?.item_header">
          <!-- Duration -->
          <span
            v-if="editable"
            class="experience-duration editable"
            :style="definition.styling?.item_duration"
            contenteditable
            @blur="updateExperience(index, 'duration', $event)"
            @keydown.enter.prevent="handleEnter($event)"
          >
            {{ experience.duration }}
          </span>
          <span
            v-else
            class="experience-duration"
            :style="definition.styling?.item_duration"
          >
            {{ experience.duration }}
          </span>

          <span class="separator">•</span>

          <!-- Title -->
          <span
            v-if="editable"
            class="experience-title editable"
            :style="definition.styling?.item_title"
            contenteditable
            @blur="updateExperience(index, 'title', $event)"
            @keydown.enter.prevent="handleEnter($event)"
          >
            {{ experience.title }}
          </span>
          <span
            v-else
            class="experience-title"
            :style="definition.styling?.item_title"
          >
            {{ experience.title }}
          </span>
        </div>

        <!-- Company -->
        <div
          v-if="editable"
          class="experience-company editable"
          :style="definition.styling?.item_company"
          contenteditable
          @blur="updateExperience(index, 'company', $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ experience.company }}
        </div>
        <div
          v-else
          class="experience-company"
          :style="definition.styling?.item_company"
        >
          {{ experience.company }}
        </div>

        <!-- Achievements -->
        <ul v-if="experience.achievements && experience.achievements.length > 0" class="achievements" :style="definition.styling?.achievements">
          <li
            v-for="(achievement, achIndex) in experience.achievements"
            :key="achIndex"
            class="achievement-item"
          >
            <span
              v-if="editable"
              class="achievement-text editable"
              contenteditable
              @blur="updateAchievement(index, achIndex, $event)"
              @keydown.enter.prevent="handleEnter($event)"
              @keydown.delete="handleDeleteAchievement(index, achIndex, $event)"
            >
              {{ achievement }}
            </span>
            <span v-else class="achievement-text">
              {{ achievement }}
            </span>
            <v-btn
              v-if="editable"
              icon="mdi-close"
              size="x-small"
              variant="text"
              class="delete-achievement"
              @click="removeAchievement(index, achIndex)"
            ></v-btn>
          </li>
          <li v-if="editable" class="achievement-item add-achievement">
            <span
              class="achievement-text editable add-text"
              contenteditable
              @blur="addAchievement(index, $event)"
              @keydown.enter.prevent="handleEnter($event)"
            ></span>
          </li>
        </ul>

        <!-- Add Achievement Button (if no achievements exist) -->
        <div v-if="editable && (!experience.achievements || experience.achievements.length === 0)" class="add-achievement-btn">
          <v-btn
            size="small"
            variant="text"
            prepend-icon="mdi-plus"
            @click="addFirstAchievement(index)"
          >
            Add Achievement
          </v-btn>
        </div>

        <!-- Remove Experience Button -->
        <div v-if="editable" class="experience-actions">
          <v-btn
            size="small"
            variant="text"
            color="error"
            prepend-icon="mdi-delete"
            @click="removeExperience(index)"
          >
            Remove Experience
          </v-btn>
        </div>
      </div>

      <!-- Add Experience Button -->
      <div v-if="editable" class="add-experience">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-plus"
          @click="addExperience"
        >
          Add Experience
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  definition: any
  sectionName: string
  sectionData: any
  editable?: boolean
}

interface Emits {
  (e: 'update:section-data', value: any): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

const containerStyles = computed(() => ({
  marginBottom: '1em',
  ...props.definition.styling?.container
}))

const experienceList = computed(() => {
  if (Array.isArray(props.sectionData.items)) {
    return props.sectionData.items
  }
  return []
})

const updateExperience = (index: number, field: string, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newExperiences = [...experienceList.value]
    newExperiences[index] = {
      ...newExperiences[index],
      [field]: target.textContent.trim()
    }
    
    emit('update:section-data', {
      type: 'experience',
      items: newExperiences
    })
  }
}

const updateAchievement = (expIndex: number, achIndex: number, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newExperiences = [...experienceList.value]
    const newAchievements = [...(newExperiences[expIndex].achievements || [])]
    
    const newValue = target.textContent.trim()
    if (newValue) {
      newAchievements[achIndex] = newValue
    } else {
      newAchievements.splice(achIndex, 1)
    }
    
    newExperiences[expIndex] = {
      ...newExperiences[expIndex],
      achievements: newAchievements
    }
    
    emit('update:section-data', {
      type: 'experience',
      items: newExperiences
    })
  }
}

const addAchievement = (expIndex: number, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newValue = target.textContent.trim()
    
    if (newValue) {
      const newExperiences = [...experienceList.value]
      const newAchievements = [...(newExperiences[expIndex].achievements || []), newValue]
      
      newExperiences[expIndex] = {
        ...newExperiences[expIndex],
        achievements: newAchievements
      }
      
      emit('update:section-data', {
        type: 'experience',
        items: newExperiences
      })
      
      // Clear the input
      target.textContent = ''
    }
  }
}

const addFirstAchievement = (expIndex: number) => {
  const newExperiences = [...experienceList.value]
  newExperiences[expIndex] = {
    ...newExperiences[expIndex],
    achievements: ['New achievement']
  }
  
  emit('update:section-data', {
    type: 'experience',
    items: newExperiences
  })
}

const removeAchievement = (expIndex: number, achIndex: number) => {
  const newExperiences = [...experienceList.value]
  const newAchievements = [...(newExperiences[expIndex].achievements || [])]
  newAchievements.splice(achIndex, 1)
  
  newExperiences[expIndex] = {
    ...newExperiences[expIndex],
    achievements: newAchievements
  }
  
  emit('update:section-data', {
    type: 'experience',
    items: newExperiences
  })
}

const addExperience = () => {
  const newExperience = {
    title: 'New Position',
    company: 'Company Name',
    duration: '2023-Present',
    achievements: ['Key achievement or responsibility']
  }
  
  const newExperiences = [...experienceList.value, newExperience]
  emit('update:section-data', {
    type: 'experience',
    items: newExperiences
  })
}

const removeExperience = (index: number) => {
  const newExperiences = [...experienceList.value]
  newExperiences.splice(index, 1)
  
  emit('update:section-data', {
    type: 'experience',
    items: newExperiences
  })
}

const handleEnter = (event: KeyboardEvent) => {
  const target = event.target as HTMLElement
  if (target && typeof target.blur === 'function') {
    target.blur()
  }
}

const handleDeleteAchievement = (expIndex: number, achIndex: number, event: KeyboardEvent) => {
  const target = event.target as HTMLElement
  if (target && target.textContent === '') {
    removeAchievement(expIndex, achIndex)
  }
}
</script>

<style scoped>
.experience-section {
  margin-bottom: 1em;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  text-transform: uppercase;
  margin-bottom: 0.3em;
  padding-bottom: 0.3em;
  border-bottom: 1.5px solid;
}

.experience-item {
  margin-bottom: 0.5em;
  padding: 0.5em;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: border-color 0.2s;
}

.experience-item:hover {
  border-color: #e0e0e0;
}

.experience-header {
  display: flex;
  align-items: center;
  gap: 0.5em;
  margin-bottom: 0.2em;
}

.experience-duration,
.experience-title {
  font-weight: bold;
  font-size: 11px;
}

.separator {
  color: #666;
}

.experience-company {
  font-weight: bold;
  font-size: 11px;
  margin-bottom: 0.2em;
  display: block;
}

.achievements {
  list-style: disc;
  margin-left: 1.2em;
  font-size: 11px;
}

.achievement-item {
  display: flex;
  align-items: flex-start;
  gap: 0.3em;
  margin-bottom: 0.1em;
}

.achievement-text {
  flex-grow: 1;
}

.delete-achievement {
  opacity: 0;
  transition: opacity 0.2s;
}

.achievement-item:hover .delete-achievement {
  opacity: 1;
}

.add-achievement .achievement-text {
  color: #999;
  font-style: italic;
}

.add-achievement .achievement-text:empty:before {
  content: '+ Add achievement';
}

.add-achievement .achievement-text:focus:before {
  content: '';
}

.editable {
  outline: none;
  border: 1px solid transparent;
  padding: 2px 4px;
  border-radius: 3px;
  transition: border-color 0.2s;
}

.editable:hover {
  border-color: #e0e0e0;
}

.editable:focus {
  border-color: #1976d2;
  background-color: rgba(25, 118, 210, 0.04);
}

.add-experience,
.add-achievement-btn,
.experience-actions {
  margin-top: 0.5em;
}

.experience-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.experience-item:hover .experience-actions {
  opacity: 1;
}
</style>