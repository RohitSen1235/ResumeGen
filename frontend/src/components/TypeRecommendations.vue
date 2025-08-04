<template>
  <div class="recommendations-container">
    <div v-if="userType === 'student'">
      <h3>Recommendations for Students/Fresh Grads</h3>
      <ul>
        <li>Highlight academic projects and coursework</li>
        <li>Include relevant internships and part-time work</li>
        <li>Showcase technical skills and certifications</li>
      </ul>
    </div>

    <div v-if="userType === 'job_seeker'">
      <h3>Recommendations for Active Job Seekers</h3>
      <ul>
        <li>Tailor resume for each job application</li>
        <li>Quantify achievements with metrics</li>
        <li>Highlight most recent and relevant experience</li>
      </ul>
    </div>

    <div v-if="userType === 'career_changer'">
      <h3>Recommendations for Career Changers</h3>
      <ul>
        <li>Focus on transferable skills</li>
        <li>Highlight relevant training/certifications</li>
        <li>Use functional resume format if needed</li>
      </ul>
    </div>

    <div v-if="userType === 'other'">
      <h3>General Resume Tips</h3>
      <ul>
        <li>Keep resume to 1-2 pages max</li>
        <li>Use action verbs to describe experience</li>
        <li>Proofread carefully for errors</li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/store/auth'

export default defineComponent({
  name: 'TypeRecommendations',
  setup() {
    const store = useAuthStore()
    const userType = computed(() => store.user?.userType)

    return { userType }
  }
})
</script>

<style scoped>
.recommendations-container {
  margin: 20px 0;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

ul {
  padding-left: 20px;
}

li {
  margin-bottom: 8px;
}
</style>
