<template>
  <div class="projects-section" :style="containerStyles">
    <!-- Section Title -->
    <h2 
      class="section-title"
      :style="definition.styling?.section_title"
    >
      {{ sectionName }}
    </h2>

    <!-- Project Items -->
    <div class="project-items">
      <div
        v-for="(project, index) in projectList"
        :key="index"
        class="project-item"
        :style="definition.styling?.item_container"
      >
        <!-- Project Title -->
        <div
          v-if="editable"
          class="project-title editable"
          :style="definition.styling?.project_title"
          contenteditable
          @blur="updateProject(index, 'title', $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ project.title }}
        </div>
        <div
          v-else
          class="project-title"
          :style="definition.styling?.project_title"
        >
          {{ project.title }}
        </div>

        <!-- Project Highlights -->
        <ul v-if="project.highlights && project.highlights.length > 0" class="highlights" :style="definition.styling?.highlights">
          <li
            v-for="(highlight, hlIndex) in project.highlights"
            :key="hlIndex"
            class="highlight-item"
          >
            <span
              v-if="editable"
              class="highlight-text editable"
              contenteditable
              @blur="updateHighlight(index, hlIndex, $event)"
              @keydown.enter.prevent="handleEnter($event)"
            >
              {{ highlight }}
            </span>
            <span v-else class="highlight-text">
              {{ highlight }}
            </span>
          </li>
        </ul>

        <!-- Remove Project Button -->
        <div v-if="editable" class="project-actions">
          <v-btn
            size="small"
            variant="text"
            color="error"
            prepend-icon="mdi-delete"
            @click="removeProject(index)"
          >
            Remove
          </v-btn>
        </div>
      </div>

      <!-- Add Project Button -->
      <div v-if="editable" class="add-project">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-plus"
          @click="addProject"
        >
          Add Project
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

const projectList = computed(() => {
  if (Array.isArray(props.sectionData.items)) {
    return props.sectionData.items
  }
  return []
})

const updateProject = (index: number, field: string, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newProjects = [...projectList.value]
    newProjects[index] = {
      ...newProjects[index],
      [field]: target.textContent.trim()
    }
    
    emit('update:section-data', {
      type: 'projects',
      items: newProjects
    })
  }
}

const updateHighlight = (projIndex: number, hlIndex: number, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newProjects = [...projectList.value]
    const newHighlights = [...(newProjects[projIndex].highlights || [])]
    
    const newValue = target.textContent.trim()
    if (newValue) {
      newHighlights[hlIndex] = newValue
    } else {
      newHighlights.splice(hlIndex, 1)
    }
    
    newProjects[projIndex] = {
      ...newProjects[projIndex],
      highlights: newHighlights
    }
    
    emit('update:section-data', {
      type: 'projects',
      items: newProjects
    })
  }
}

const addProject = () => {
  const newProject = {
    title: 'New Project',
    highlights: ['Project description or key achievement']
  }
  
  const newProjects = [...projectList.value, newProject]
  emit('update:section-data', {
    type: 'projects',
    items: newProjects
  })
}

const removeProject = (index: number) => {
  const newProjects = [...projectList.value]
  newProjects.splice(index, 1)
  
  emit('update:section-data', {
    type: 'projects',
    items: newProjects
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
.projects-section {
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

.project-item {
  margin-bottom: 0.5em;
  padding: 0.5em;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: border-color 0.2s;
}

.project-item:hover {
  border-color: #e0e0e0;
}

.project-title {
  font-weight: bold;
  font-size: 11px;
  margin-bottom: 0.2em;
}

.highlights {
  list-style: disc;
  margin-left: 1.2em;
  font-size: 11px;
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

.project-actions {
  margin-top: 0.5em;
  opacity: 0;
  transition: opacity 0.2s;
}

.project-item:hover .project-actions {
  opacity: 1;
}

.add-project {
  margin-top: 0.5em;
}
</style>