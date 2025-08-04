<template>
  <div class="d-flex justify-center">
    <v-btn
      @click="handleLinkedInLogin"
      variant="text"
      :loading="loading"
      class="pa-0"
      style="height: auto; min-height: auto; max-width: 300px;"
    >
      <img 
        src="@/assets/Sign-In-Large---Active.png" 
        alt="Sign in with LinkedIn" 
        style="width: 100%; height: auto;"
      />
    </v-btn>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const loading = ref(false)

const handleLinkedInLogin = async () => {
  try {
    loading.value = true
    await auth.linkedinLogin()
  } catch (err: any) {
    console.error('LinkedIn login failed:', err)
  } finally {
    loading.value = false
  }
}
</script>
