<template>
  <div class="user-type-selector">
    <h3>Which describes you?</h3>
    <v-radio-group v-model="selectedType">
      <v-radio label="Student/Fresh grad" value="student"></v-radio>
      <v-radio label="Active job seeker" value="job_seeker"></v-radio>
      <v-radio label="Career changer" value="career_changer"></v-radio>
      <v-radio label="Other" value="other"></v-radio>
    </v-radio-group>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue'
import { useAuthStore } from '@/store/auth'

export default defineComponent({
  name: 'UserTypeSelector',
  setup() {
    const store = useAuthStore()
    const selectedType = ref(store.user?.userType || '')

    watch(selectedType, (newVal) => {
      store.setUserType(newVal)
    })

    return { selectedType }
  }
})
</script>

<style scoped>
.user-type-selector {
  margin: 20px 0;
}
</style>
