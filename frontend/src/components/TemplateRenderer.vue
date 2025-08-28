<template>
  <div class="template-renderer" :style="containerStyles">
    <!-- Header Section -->
    <HeaderSection
      v-if="templateDefinition.sections?.header"
      :definition="templateDefinition.sections.header"
      :personal-info="personalInfo"
      :editable="editable"
      @update:personal-info="$emit('update:personal-info', $event)"
    />

    <!-- Dynamic Sections -->
    <template v-for="sectionName in sectionOrder" :key="sectionName">
      <component
        v-if="templateDefinition.sections?.[sectionName.toLowerCase()] && resumeData[sectionName]"
        :is="getSectionComponent(templateDefinition.sections[sectionName.toLowerCase()].type)"
        :definition="templateDefinition.sections[sectionName.toLowerCase()]"
        :section-name="sectionName"
        :section-data="resumeData[sectionName]"
        :editable="editable"
        @update:section-data="onSectionUpdate(sectionName, $event)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import HeaderSection from './sections/HeaderSection.vue'
import TextSection from './sections/TextSection.vue'
import SkillsSection from './sections/SkillsSection.vue'
import ExperienceSection from './sections/ExperienceSection.vue'
import EducationSection from './sections/EducationSection.vue'
import ProjectsSection from './sections/ProjectsSection.vue'
import AchievementsSection from './sections/AchievementsSection.vue'
import CertificationsSection from './sections/CertificationsSection.vue'

interface Props {
  templateDefinition: any
  resumeData: any
  personalInfo: any
  editable?: boolean
}

interface Emits {
  (e: 'update:resume-data', value: any): void
  (e: 'update:personal-info', value: any): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: false
})

const emit = defineEmits<Emits>()

// Define the order of sections as they should appear
const sectionOrder = [
  'Professional Summary',
  'Key Skills', 
  'Professional Experience',
  'Education',
  'Projects',
  'Key Achievements',
  'Certifications',
  'Others'
]

// Computed styles for the container
const containerStyles = computed(() => {
  const colors = props.templateDefinition?.colors || {}
  const typography = props.templateDefinition?.typography || {}
  const spacing = props.templateDefinition?.spacing || {}
  
  return {
    fontFamily: typography.font_family || 'Arial, sans-serif',
    fontSize: typography.body_size || '11px',
    lineHeight: typography.line_height || '1.6',
    color: colors.text || '#000000',
    backgroundColor: colors.background || '#ffffff',
    padding: props.templateDefinition?.layout?.columns?.[0]?.padding || '0.75in',
    maxWidth: '8.5in',
    minHeight: '11in',
    margin: '0 auto',
    boxShadow: '0 0 10px rgba(0,0,0,0.1)',
    ...spacing
  }
})

// Get the appropriate component for each section type
const getSectionComponent = (sectionType: string) => {
  const componentMap: Record<string, any> = {
    'text': TextSection,
    'skills': SkillsSection,
    'tags': SkillsSection, // Skills can be displayed as tags
    'list': ExperienceSection, // Default list component
    'experience': ExperienceSection,
    'education': EducationSection,
    'projects': ProjectsSection,
    'achievements': AchievementsSection,
    'certifications': CertificationsSection
  }
  
  return componentMap[sectionType] || TextSection
}

// Handle section updates
const onSectionUpdate = (sectionName: string, newData: any) => {
  const updatedResumeData = {
    ...props.resumeData,
    [sectionName]: newData
  }
  emit('update:resume-data', updatedResumeData)
}
</script>

<style scoped>
.template-renderer {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Print styles */
@media print {
  .template-renderer {
    box-shadow: none;
    margin: 0;
    max-width: none;
  }
}
</style>