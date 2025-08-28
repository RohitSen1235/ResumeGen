<template>
  <div class="certifications-section" :style="containerStyles">
    <!-- Section Title -->
    <h2 
      class="section-title"
      :style="definition.styling?.section_title"
    >
      {{ sectionName }}
    </h2>

    <!-- Certifications List -->
    <ul class="certifications-list" :style="certificationsListStyles">
      <li
        v-for="(certification, index) in certificationsList"
        :key="index"
        class="certification-item"
        :style="definition.styling?.cert_item"
      >
        <span
          v-if="editable"
          class="certification-text editable"
          contenteditable
          @blur="updateCertification(index, $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ certification }}
        </span>
        <span
          v-else
          class="certification-text"
        >
          {{ certification }}
        </span>
        <v-btn
          v-if="editable"
          icon="mdi-close"
          size="x-small"
          variant="text"
          class="delete-certification"
          @click="removeCertification(index)"
        ></v-btn>
      </li>

      <!-- Add Certification -->
      <li v-if="editable" class="certification-item add-certification">
        <span
          class="certification-text editable add-text"
          contenteditable
          @blur="addCertification($event)"
          @keydown.enter.prevent="handleEnter($event)"
        ></span>
      </li>
    </ul>
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

const certificationsListStyles = computed(() => {
  if (props.definition.layout === 'columns') {
    return {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '0.3em',
      listStyle: 'disc',
      marginLeft: '1.2em',
      fontSize: '11px'
    }
  }
  return {
    listStyle: 'disc',
    marginLeft: '1.2em',
    fontSize: '11px'
  }
})

const certificationsList = computed(() => {
  if (Array.isArray(props.sectionData.items)) {
    return props.sectionData.items
  }
  return []
})

const updateCertification = (index: number, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newCertifications = [...certificationsList.value]
    const newValue = target.textContent.trim()
    
    if (newValue) {
      newCertifications[index] = newValue
    } else {
      newCertifications.splice(index, 1)
    }
    
    emit('update:section-data', {
      type: 'certifications',
      items: newCertifications
    })
  }
}

const addCertification = (event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    const newValue = target.textContent.trim()
    
    if (newValue) {
      const newCertifications = [...certificationsList.value, newValue]
      emit('update:section-data', {
        type: 'certifications',
        items: newCertifications
      })
      
      // Clear the input
      target.textContent = ''
    }
  }
}

const removeCertification = (index: number) => {
  const newCertifications = [...certificationsList.value]
  newCertifications.splice(index, 1)
  
  emit('update:section-data', {
    type: 'certifications',
    items: newCertifications
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
.certifications-section {
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

.certifications-list {
  list-style: disc;
  margin-left: 1.2em;
  font-size: 11px;
}

.certification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.3em;
  margin-bottom: 0.2em;
}

.certification-text {
  flex-grow: 1;
}

.delete-certification {
  opacity: 0;
  transition: opacity 0.2s;
}

.certification-item:hover .delete-certification {
  opacity: 1;
}

.add-certification .certification-text {
  color: #999;
  font-style: italic;
}

.add-certification .certification-text:empty:before {
  content: '+ Add certification';
}

.add-certification .certification-text:focus:before {
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