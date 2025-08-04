<template>
  <v-container class="d-flex align-center justify-center" style="min-height: 100vh;">
    <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="500">
      <v-card-title class="d-flex align-center justify-center flex-column mb-4">
        <img src="@/assets/logo-dark.svg" alt="Resume Genie Logo" class="mb-4" style="width: 300px; height: auto;">
        <div class="text-h5">LinkedIn Authentication</div>
      </v-card-title>

      <div class="text-center">
        <v-progress-circular
          v-if="loading"
          indeterminate
          color="primary"
          size="64"
          class="mb-4"
        ></v-progress-circular>
        
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <v-alert
          v-if="success"
          type="success"
          variant="tonal"
          class="mb-4"
        >
          {{ success }}
        </v-alert>

        <p v-if="loading" class="text-body-1">
          Processing LinkedIn authentication...
        </p>

        <v-btn
          v-if="error"
          @click="goToLogin"
          color="orange-lighten-2"
          variant="outlined"
          class="mt-4"
        >
          Back to Login
        </v-btn>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const error = ref('')
const success = ref('')

const goToLogin = () => {
  router.push('/login')
}

onMounted(async () => {
  try {
    const code = route.query.code as string
    const state = route.query.state as string

    if (!code || !state) {
      throw new Error('Missing authorization code or state parameter')
    }

    // Handle LinkedIn callback
    const user = await auth.handleLinkedinCallback(code, state)
    
    success.value = 'LinkedIn authentication successful! Redirecting...'
    
    // Redirect based on profile status
    setTimeout(() => {
      if (auth.hasProfile) {
        router.push('/resume-builder')
      } else {
        router.push('/profile')
      }
    }, 2000)

  } catch (err: any) {
    console.error('LinkedIn callback error:', err)
    error.value = typeof err === 'string' ? err : 'LinkedIn authentication failed. Please try again.'
  } finally {
    loading.value = false
  }
})
</script>
