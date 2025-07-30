<template>
  <div class="template-management">
    <h2>Template Management</h2>
    <div class="template-list">
      <!-- Template list will be implemented here -->
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { useAuthStore } from '@/store/auth'

export default defineComponent({
  name: 'TemplateManagement',
  setup() {
    const auth = useAuthStore()
    return { auth }
  }
})
</script>

<style scoped>
.template-management {
  padding: 2rem;
}

.template-list {
  margin-top: 1rem;
}
</style>
