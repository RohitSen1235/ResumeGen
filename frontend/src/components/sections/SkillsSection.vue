<template>
  <div class="skills-section" :style="containerStyles">
    <!-- Section Title -->
    <h2 
      class="section-title"
      :style="definition.styling?.section_title"
    >
      {{ sectionName }}
    </h2>

    <!-- Skills Container -->
    <div class="skills-container" :style="definition.styling?.skills_container">
      <!-- Skills Label (if defined in template) -->
      <span 
        v-if="definition.styling?.skills_label"
        class="skills-label"
        :style="definition.styling.skills_label"
      >
        Technical Skills:
      </span>

      <!-- Skills List -->
      <div class="skills-list" :style="skillsListStyles">
        <template v-if="editable">
          <span
            v-for="(skill, index) in skillsList"
            :key="index"
            class="skill-item editable"
            :style="definition.styling?.skill_item"
            contenteditable
            @blur="updateSkill(index, $event)"
            @keydown.enter.prevent="handleEnter($event)"
            @keydown.delete="handleDelete(index, $event)"
          >
            {{ skill }}
          </span>
          <span
            class="skill-item add-skill"
            :style="definition.styling?.skill_item"
            contenteditable
            @blur="addSkill($event)"
            @keydown.enter.prevent="handleEnter($event)"
            placeholder="Add skill..."
          >
          </span>
        </template>
        <template v-else>
          <span
            v-for="(skill, index) in skillsList"
            :key="index"
            class="skill-item"
            :style="definition.styling?.skill_item"
          >
            {{ skill }}{{ index < skillsList.length - 1 ? ', ' : '' }}
          </span>
        </template>
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

const skillsListStyles = computed(() => {
  if (props.definition.layout === 'inline') {
    return {
      display: 'flex',
      flexWrap: 'wrap' as const,
      gap: '0.5em'
    }
  } else if (props.definition.layout === 'columns') {
    return {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
      gap: '0.3em'
    }
  }
  return {}
})

const skillsList = computed(() => {
  if (Array.isArray(props.sectionData.items)) {
    return props.sectionData.items
  }
  return []
})

const updateSkill = (index: number, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newSkills = [...skillsList.value]
    const newValue = target.textContent.trim()
    
    if (newValue) {
      newSkills[index] = newValue
    } else {
      // Remove empty skill
      newSkills.splice(index, 1)
    }
    
    emit('update:section-data', {
      type: 'skills',
      items: newSkills
    })
  }
}

const addSkill = (event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newValue = target.textContent.trim()
    
    if (newValue) {
      const newSkills = [...skillsList.value, newValue]
      emit('update:section-data', {
        type: 'skills',
        items: newSkills
      })
      
      // Clear the input
      target.textContent = ''
    }
  }
}

const handleEnter = (event: KeyboardEvent) => {
  const target = event.target as HTMLElement
  if (target && typeof target.blur === 'function') {
    target.blur()
  }
}

const handleDelete = (index: number, event: KeyboardEvent) => {
  const target = event.target as HTMLElement
  if (target && target.textContent === '') {
    // If the field is empty and delete is pressed, remove the skill
    const newSkills = [...skillsList.value]
    newSkills.splice(index, 1)
    emit('update:section-data', {
      type: 'skills',
      items: newSkills
    })
  }
}
</script>

<style scoped>
.skills-section {
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

.skills-container {
  margin-bottom: 0.5em;
}

.skills-label {
  font-weight: bold;
  margin-right: 0.5em;
}

.skills-list {
  display: inline;
}

.skill-item {
  font-size: 11px;
  display: inline;
}

.skill-item.editable {
  outline: none;
  border: 1px solid transparent;
  padding: 2px 4px;
  border-radius: 3px;
  transition: border-color 0.2s;
  margin: 0 2px;
  background-color: rgba(0, 0, 0, 0.05);
}

.skill-item.editable:hover {
  border-color: #e0e0e0;
}

.skill-item.editable:focus {
  border-color: #1976d2;
  background-color: rgba(25, 118, 210, 0.04);
}

.skill-item.add-skill {
  color: #999;
  font-style: italic;
  min-width: 80px;
  display: inline-block;
}

.skill-item.add-skill:empty:before {
  content: '+ Add skill';
}

.skill-item.add-skill:focus:before {
  content: '';
}
</style>