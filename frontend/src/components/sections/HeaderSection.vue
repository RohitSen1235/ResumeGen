<template>
  <div class="header-section" :style="containerStyles">
    <!-- Name -->
    <div
      v-if="editable"
      class="editable-field name-field"
      :style="definition.styling?.name_style"
      contenteditable
      @blur="handleBlur('name', $event)"
      @keydown.enter.prevent="handleEnter($event)"
    >
      {{ personalInfo.name }}
    </div>
    <div 
      v-else
      class="name-field"
      :style="definition.styling?.name_style"
    >
      {{ personalInfo.name }}
    </div>

    <!-- Professional Title -->
    <div 
      v-if="personalInfo.professional_title"
      class="title-field"
      :style="definition.styling?.title_style"
    >
      <span 
        v-if="editable"
        contenteditable
        @blur="handleBlur('professional_title', $event)"
        @keydown.enter.prevent="handleEnter($event)"
      >
        {{ personalInfo.professional_title }}
      </span>
      <span v-else>
        {{ personalInfo.professional_title }}
      </span>
    </div>

    <!-- Contact Information -->
    <div class="contact-info" :style="definition.styling?.contact_style">
      <div class="contact-item" v-if="personalInfo.email">
        <v-icon icon="mdi-email" size="small" class="contact-icon"></v-icon>
        <span 
          v-if="editable"
          contenteditable
          @blur="handleBlur('email', $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ personalInfo.email }}
        </span>
        <span v-else>{{ personalInfo.email }}</span>
      </div>

      <div class="contact-item" v-if="personalInfo.phone">
        <v-icon icon="mdi-phone" size="small" class="contact-icon"></v-icon>
        <span 
          v-if="editable"
          contenteditable
          @blur="handleBlur('phone', $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ personalInfo.phone }}
        </span>
        <span v-else>{{ personalInfo.phone }}</span>
      </div>

      <div class="contact-item" v-if="personalInfo.location">
        <v-icon icon="mdi-map-marker" size="small" class="contact-icon"></v-icon>
        <span 
          v-if="editable"
          contenteditable
          @blur="handleBlur('location', $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ personalInfo.location }}
        </span>
        <span v-else>{{ personalInfo.location }}</span>
      </div>

      <div class="contact-item" v-if="personalInfo.linkedin">
        <v-icon icon="mdi-linkedin" size="small" class="contact-icon"></v-icon>
        <span 
          v-if="editable"
          contenteditable
          @blur="handleBlur('linkedin', $event)"
          @keydown.enter.prevent="handleEnter($event)"
        >
          {{ personalInfo.linkedin }}
        </span>
        <span v-else>{{ personalInfo.linkedin }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  definition: any
  personalInfo: any
  editable?: boolean
}

interface Emits {
  (e: 'update:personal-info', value: any): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

const containerStyles = computed(() => ({
  ...props.definition.styling?.container,
  marginBottom: '1em'
}))

const updatePersonalInfo = (field: string, value: string | null) => {
  if (value !== null) {
    emit('update:personal-info', {
      ...props.personalInfo,
      [field]: value.trim()
    })
  }
}

const handleBlur = (field: string, event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    updatePersonalInfo(field, target.textContent)
  }
}

const handleEnter = (event: KeyboardEvent) => {
  const target = event.target as HTMLElement
  if (target && typeof target.blur === 'function') {
    target.blur()
  }
}
</script>

<style scoped>
.header-section {
  margin-bottom: 1.5em;
}

.name-field {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 0.3em;
  text-transform: uppercase;
}

.title-field {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 0.5em;
}

.contact-info {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.2em;
  font-size: 11px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 0.3em;
}

.contact-icon {
  flex-shrink: 0;
}

.editable-field {
  outline: none;
  border: 1px solid transparent;
  padding: 2px;
  border-radius: 3px;
  transition: border-color 0.2s;
}

.editable-field:hover {
  border-color: #e0e0e0;
}

.editable-field:focus {
  border-color: #1976d2;
  background-color: rgba(25, 118, 210, 0.04);
}

[contenteditable] {
  outline: none;
  border: 1px solid transparent;
  padding: 1px 3px;
  border-radius: 3px;
  transition: border-color 0.2s;
}

[contenteditable]:hover {
  border-color: #e0e0e0;
}

[contenteditable]:focus {
  border-color: #1976d2;
  background-color: rgba(25, 118, 210, 0.04);
}
</style>