<template>
  <v-container class="fill-height pa-0" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" md="8" lg="6">
        <v-card class="elevation-12 rounded-xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-card-title class="d-flex align-center justify-center flex-column pt-8 pb-4">
            <img src="@/assets/logo-dark.svg" alt="Resume Genie Logo" class="mb-4" style="width: 200px; height: auto;">
            <div class="text-h5 font-weight-medium text-grey-darken-3">LinkedIn Authentication</div>
          </v-card-title>
          <v-card-text class="text-center pa-8">
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
              icon="mdi-alert-circle-outline"
            >
              {{ error }}
            </v-alert>

            <v-alert
              v-if="success"
              type="success"
              variant="tonal"
              class="mb-4"
              icon="mdi-check-circle-outline"
            >
              {{ success }}
            </v-alert>

            <p v-if="loading" class="text-body-1 text-grey-darken-1">
              Processing LinkedIn authentication, please wait...
            </p>

            <v-btn
              v-if="error"
              @click="goToLogin"
              color="orange-lighten-2"
              class="mt-4"
              size="large"
              rounded="lg"
              elevation="4"
            >
              Back to Login
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
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
    
    // Redirect based on onboarding completion status
    setTimeout(() => {
      if (auth.hasCompletedOnboarding) {
        router.push('/resume-builder')
      } else {
        router.push('/onboarding?source=linkedin')
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
