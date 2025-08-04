<template>
  <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="500">
    <v-card-title class="d-flex align-center justify-center flex-column mb-4">
      <img src="@/assets/logo-dark.svg" alt="Resume Genie Logo" class="mb-4" style="width: 300px; height: auto;">
      <div class="text-h5">Reset Password</div>
    </v-card-title>

    <v-form @submit.prevent="handleSubmit" v-model="isValid">
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        :rules="[
          v => !!v || 'Email is required',
          v => /.+@.+\..+/.test(v) || 'Email must be valid'
        ]"
        variant="outlined"
        density="comfortable"
        class="mb-4"
      ></v-text-field>

      <v-alert
        v-if="error"
        type="error"
        variant="tonal"
        class="mb-4"
        closable
      >
        {{ error }}
      </v-alert>

      <v-alert
        v-if="success"
        type="success"
        variant="tonal"
        class="mb-4"
      >
        Password reset email sent!
      </v-alert>

      <div class="d-flex flex-column gap-4">
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

        <div class="text-center">
          Remember your password?
          <a href="/login" class="text-primary">
            Login
          </a>
        </div>
      </div>
    </v-form>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import type { Ref } from 'vue'

const auth = useAuthStore()
const router = useRouter()

const email: Ref<string> = ref('')
const isValid: Ref<boolean> = ref(false)
const error: Ref<string> = ref('')
const success: Ref<boolean> = ref(false)
const loading: Ref<boolean> = ref(false)

const handleSubmit = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    error.value = ''
    success.value = false
    
    await auth.forgotPassword(email.value)
    success.value = true
  } catch (err: any) {
    error.value = typeof err === 'string' ? err : 'Failed to send reset email'
  } finally {
    loading.value = false
  }
}

defineExpose({
  isValid,
  handleSubmit
})
</script>
