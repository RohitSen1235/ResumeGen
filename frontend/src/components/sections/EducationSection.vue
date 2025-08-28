<template>
  <div class="education-section" :style="containerStyles">
    <!-- Section Title -->
    <h2 
      class="section-title"
      :style="definition.styling?.section_title"
    >
      {{ sectionName }}
    </h2>

    <!-- Education Items -->
    <div class="education-items">
      <div
        v-for="(education, index) in educationList"
        :key="index"
        class="education-item"
        :style="definition.styling?.item_container"
      >
        <!-- Education Header -->
        <div class="education-header" :style="definition.styling?.item_header">
          <!-- Year -->
          <span
            v-if="editable"
            class="education-year editable"
            :style="definition.styling?.item_year"
            contenteditable
            @blur="updateEducation(index, 'year', $event)"
            @keydown.enter.prevent="handleEnter($event)"
          >
            {{ education.year }}
          </span>
          <span
            v-else
            class="education-year"
            :style="definition.styling?.item_year"
          >
            {{ education.year }}
          </span>

          <span class="separator">•</span>

          <!-- Degree -->
          <span
            v-if="editable"
            class="education-degree editable"
            :style="definition.styling?.item_degree"
            contenteditable
            @blur="updateEducation(index, 'degree', $event)"
            @keydown.enter.prevent="handleEnter($event)"
          >
            {{ education.degree }}
          </span>
          <span
            v-else
            class="education-degree"
            :style="definition.styling?.item_degree"
          >
            {{ education.degree }}
          </span>
        </div>

        <!-- Institution -->
        <div
          v-if="editable"
          class="education-institution editable"
          :style="definition.styling?.item_institution"
          contenteditable
          @blur="updateEducation(index, 'institution', $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ education.institution }}
        </div>
        <div
          v-else
          class="education-institution"
          :style="definition.styling?.item_institution"
        >
          {{ education.institution }}
        </div>

        <!-- Details -->
        <ul v-if="education.details && education.details.length > 0" class="details" :style="definition.styling?.details">
          <li
            v-for="(detail, detIndex) in education.details"
            :key="detIndex"
            class="detail-item"
          >
            <span
              v-if="editable"
              class="detail-text editable"
              contenteditable
              @blur="updateDetail(index, detIndex, $event)"
              @keydown.enter.prevent="handleEnter($event)"
            >
              {{ detail }}
            </span>
            <span v-else class="detail-text">
              {{ detail }}
            </span>
          </li>
        </ul>

        <!-- Remove Education Button -->
        <div v-if="editable" class="education-actions">
          <v-btn
            size="small"
            variant="text"
            color="error"
            prepend-icon="mdi-delete"
            @click="removeEducation(index)"
          >
            Remove
          </v-btn>
        </div>
      </div>

      <!-- Add Education Button -->
      <div v-if="editable" class="add-education">
        <v-btn
          color="primary"
          variant="outlined"
          prepend-icon="mdi-plus"
          @click="addEducation"
        >
          Add Education
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

const educationList = computed(() => {
  if (Array.isArray(props.sectionData.items)) {
    return props.sectionData.items
  }
  return []
})

const updateEducation = (index: number, field: string, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newEducations = [...educationList.value]
    newEducations[index] = {
      ...newEducations[index],
      [field]: target.textContent.trim()
    }
    
    emit('update:section-data', {
      type: 'education',
      items: newEducations
    })
  }
}

const updateDetail = (eduIndex: number, detIndex: number, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newEducations = [...educationList.value]
    const newDetails = [...(newEducations[eduIndex].details || [])]
    
    const newValue = target.textContent.trim()
    if (newValue) {
      newDetails[detIndex] = newValue
    } else {
      newDetails.splice(detIndex, 1)
    }
    
    newEducations[eduIndex] = {
      ...newEducations[eduIndex],
      details: newDetails
    }
    
    emit('update:section-data', {
      type: 'education',
      items: newEducations
    })
  }
}

const addEducation = () => {
  const newEducation = {
    degree: 'Bachelor of Science',
    institution: 'University Name',
    year: '2020',
    details: []
  }
  
  const newEducations = [...educationList.value, newEducation]
  emit('update:section-data', {
    type: 'education',
    items: newEducations
  })
}

const removeEducation = (index: number) => {
  const newEducations = [...educationList.value]
  newEducations.splice(index, 1)
  
  emit('update:section-data', {
    type: 'education',
    items: newEducations
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
.education-section {
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

.education-item {
  margin-bottom: 0.5em;
  padding: 0.5em;
  border: 1px solid transparent;
  border-radius: 4px;
  transition: border-color 0.2s;
}

.education-item:hover {
  border-color: #e0e0e0;
}

.education-header {
  display: flex;
  align-items: center;
  gap: 0.5em;
  margin-bottom: 0.2em;
}

.education-year,
.education-degree {
  font-weight: bold;
  font-size: 11px;
}

.separator {
  color: #666;
}

.education-institution {
  font-weight: bold;
  font-size: 11px;
  margin-bottom: 0.2em;
  display: block;
}

.details {
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

.education-actions {
  margin-top: 0.5em;
  opacity: 0;
  transition: opacity 0.2s;
}

.education-item:hover .education-actions {
  opacity: 1;
}

.add-education {
  margin-top: 0.5em;
}
</style>