<template>
  <div class="achievements-section" :style="containerStyles">
    <!-- Section Title -->
    <h2 
      class="section-title"
      :style="definition.styling?.section_title"
    >
      {{ sectionName }}
    </h2>

    <!-- Achievements Container -->
    <div class="achievements-container" :style="achievementsContainerStyles">
      <div
        v-for="(achievement, index) in achievementsList"
        :key="index"
        class="achievement-item"
        :style="definition.styling?.achievement_item"
      >
        <span
          v-if="definition.styling?.achievement_icon"
          class="achievement-icon"
          :style="definition.styling.achievement_icon"
        >
          🏆
        </span>
        <span
          v-if="editable"
          class="achievement-text editable"
          contenteditable
          @blur="updateAchievement(index, $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ achievement }}
        </span>
        <span
          v-else
          class="achievement-text"
        >
          {{ achievement }}
        </span>
        <v-btn
          v-if="editable"
          icon="mdi-close"
          size="x-small"
          variant="text"
          class="delete-achievement"
          @click="removeAchievement(index)"
        ></v-btn>
      </div>

      <!-- Add Achievement -->
      <div v-if="editable" class="achievement-item add-achievement">
        <span
          class="achievement-text editable add-text"
          contenteditable
          @blur="addAchievement($event)"
          @keydown.enter.prevent="handleEnter($event)"
        ></span>
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

const achievementsContainerStyles = computed(() => {
  if (props.definition.layout === 'columns') {
    return {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '0.5em',
      marginBottom: '0.5em',
      ...props.definition.styling?.achievements_container
    }
  }
  return {
    marginBottom: '0.5em',
    ...props.definition.styling?.achievements_container
  }
})

const achievementsList = computed(() => {
  if (Array.isArray(props.sectionData.items)) {
    return props.sectionData.items
  }
  return []
})

const updateAchievement = (index: number, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newAchievements = [...achievementsList.value]
    const newValue = target.textContent.trim()
    
    if (newValue) {
      newAchievements[index] = newValue
    } else {
      newAchievements.splice(index, 1)
    }
    
    emit('update:section-data', {
      type: 'achievements',
      items: newAchievements
    })
  }
}

const addAchievement = (event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newValue = target.textContent.trim()
    
    if (newValue) {
      const newAchievements = [...achievementsList.value, newValue]
      emit('update:section-data', {
        type: 'achievements',
        items: newAchievements
      })
      
      // Clear the input
      target.textContent = ''
    }
  }
}

const removeAchievement = (index: number) => {
  const newAchievements = [...achievementsList.value]
  newAchievements.splice(index, 1)
  
  emit('update:section-data', {
    type: 'achievements',
    items: newAchievements
  })
}

const handleEnter = (event: KeyboardEvent) => {
  const target = event.target as HTMLElement
  if (target && typeof target.blur === 'function') {
    target.blur()
  }
}
</script>

<style scoped>
.achievements-section {
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

.achievement-item {
  display: flex;
  align-items: flex-start;
  gap: 0.3em;
  margin-bottom: 0.2em;
  font-size: 11px;
}

.achievement-icon {
  flex-shrink: 0;
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
</style>