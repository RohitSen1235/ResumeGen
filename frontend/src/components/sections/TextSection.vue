<template>
  <div class="text-section" :style="containerStyles">
    <!-- Section Title -->
    <h2 
      class="section-title"
      :style="definition.styling?.section_title"
    >
      {{ sectionName }}
    </h2>

    <!-- Section Content -->
    <div 
      v-if="editable"
      class="editable-content"
      :style="definition.styling?.content"
      contenteditable
      @blur="handleContentUpdate"
      @keydown="handleKeydown"
    >
      {{ sectionData.content }}
    </div>
    <div 
      v-else
      class="content"
      :style="definition.styling?.content"
    >
      {{ sectionData.content }}
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

const handleContentUpdate = (event: Event) => {
  const target = event.target as HTMLElement
  if (target && target.textContent !== null) {
    emit('update:section-data', {
      type: 'text',
      content: target.textContent.trim()
    })
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  // Allow normal text editing behavior
  if (event.key === 'Enter' && !event.shiftKey) {
    // Allow line breaks with Shift+Enter, but prevent default Enter behavior
    event.preventDefault()
    const target = event.target as HTMLElement
    if (target) {
      target.blur()
    }
  }
}
</script>

<style scoped>
.text-section {
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

.content,
.editable-content {
  font-size: 11px;
  line-height: 1.6;
  margin-bottom: 0.5em;
}

.editable-content {
  outline: none;
  border: 1px solid transparent;
  padding: 4px;
  border-radius: 3px;
  transition: border-color 0.2s;
  min-height: 1.5em;
}

.editable-content:hover {
  border-color: #e0e0e0;
}

.editable-content:focus {
  border-color: #1976d2;
  background-color: rgba(25, 118, 210, 0.04);
}

.editable-content:empty:before {
  content: 'Click to edit...';
  color: #999;
  font-style: italic;
}
</style>