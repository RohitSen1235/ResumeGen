<template>
  <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="500">
    <v-card-title class="d-flex align-center justify-center flex-column mb-4">
      <img src="@/assets/logo-dark.svg" alt="Resume Genie Logo" class="mb-4" style="width: 300px; height: auto;">
      <div class="text-h5">Reset Password</div>
    </v-card-title>

    <v-card-text>
      <v-alert
        v-if="successMessage"
        type="success"
        variant="tonal"
        class="mb-4"
        closable
      >
        {{ successMessage }}
      </v-alert>

      <v-form @submit.prevent="handleSubmit" v-model="isValid">
        <v-card-text class="text-center text-body-1 mb-4">
          Resetting password for: <strong>{{ email }}</strong>
        </v-card-text>

        <v-text-field
          v-model="password"
          label="New Password"
          type="password"
          :rules="[v => !!v || 'Password is required']"
          variant="outlined"
          density="comfortable"
          class="mb-4"
        />

        <v-text-field
          v-model="confirmPassword"
          label="Confirm New Password"
          type="password"
          :rules="[
            v => !!v || 'Password confirmation is required',
            v => v === password || 'Passwords must match'
          ]"
          variant="outlined"
          density="comfortable"
          class="mb-6"
        />

        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          class="mb-4"
          closable
        >
          {{ error }}
        </v-alert>

        <v-btn
          type="submit"
          color="orange-lighten-2"
          block
          :loading="loading"
          :disabled="!isValid"
          rounded="pill"
        >
          Reset Password
        </v-btn>

        <div class="text-center mt-4">
          Remember your password?
          <a href="/login" class="text-primary">
            Login
          </a>
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const successMessage = ref('')
const error = ref('')
const isValid = ref(false)

onMounted(async () => {
  try {
    const token = route.query.token as string
    if (!token) {
      router.push({ name: 'forgot-password' })
      return
    }
    
    loading.value = true
    const userEmail = await auth.verifyResetToken(token)
    email.value = userEmail
  } catch (err: any) {
    error.value = typeof err === 'string' ? err : 'Invalid or expired token'
    setTimeout(() => {
      router.push({ name: 'forgot-password' })
    }, 3000)
  } finally {
    loading.value = false
  }
})

const handleSubmit = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    error.value = ''
    const token = route.query.token as string
    await auth.resetPassword(token, password.value)
    successMessage.value = 'Password reset successfully! Redirecting to login...'
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 3000)
  } catch (err: any) {
    error.value = typeof err === 'string' ? err : 'Password reset failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
