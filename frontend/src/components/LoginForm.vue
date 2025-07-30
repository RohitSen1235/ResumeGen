<template>
  <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="500">
    <v-card-title class="d-flex align-center justify-center flex-column mb-4">
      <img src="@/assets/logo-dark.svg" alt="Resume Genie Logo" class="mb-4" style="width: 300px; height: auto;">
      <div class="text-h5">Login</div>
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

      <v-text-field
        v-model="password"
        label="Password"
        type="password"
        :rules="[v => !!v || 'Password is required']"
        variant="outlined"
        density="comfortable"
        class="mb-6"
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

      <div class="d-flex flex-column gap-4">
        <v-btn
          type="submit"
          color="primary"
          block
          :loading="loading"
          :disabled="!isValid"
          rounded="pill"
        >
          Login
        </v-btn>

        <v-divider class="my-4">
          <span class="text-medium-emphasis">OR</span>
        </v-divider>

        <v-btn
          @click="handleLinkedInLogin"
          variant="text"
          block
          :loading="loading"
          class="pa-0"
          style="height: auto; min-height: auto;"
        >
          <img 
            src="@/assets/Sign-In-Large---Active.png" 
            alt="Sign in with LinkedIn" 
            style="width: 100%; max-width: 300px; height: auto;"
          />
        </v-btn>

        <div class="text-center">
          Don't have an account?
          <a href="/signup" class="text-primary">
            Sign up
          </a>
        </div>
        <div class="text-center mt-2">
          <a href="/forgot-password" class="text-primary">
            Forgot password?
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

const auth = useAuthStore()
const router = useRouter()

interface LoginForm {
  email: string
  password: string
  isValid: boolean
  error: string
  loading: boolean
}

const email = ref<string>('')
const password = ref<string>('')
const isValid = ref<boolean>(false)
const error = ref<string>('')
const loading = ref<boolean>(false)

const handleSubmit = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    error.value = '' // Clear any previous errors
    await auth.login(email.value, password.value)

    if (auth.hasProfile) {
      router.push('/resume-builder')
    } else {
      router.push('/')
    }
  } catch (err: any) {
    // Display the actual error message from the backend
    error.value = typeof err === 'string' ? err : 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}

const handleLinkedInLogin = async () => {
  try {
    loading.value = true
    error.value = ''
    await auth.linkedinLogin()
  } catch (err: any) {
    error.value = typeof err === 'string' ? err : 'LinkedIn login failed'
  } finally {
    loading.value = false
  }
}

const handleForgotPassword = async () => {
  if (!email.value) {
    error.value = 'Please enter your email address'
    return
  }

  try {
    loading.value = true
    error.value = ''
    await auth.forgotPassword(email.value)
    error.value = 'Password reset email sent. Please check your inbox.'
  } catch (err: any) {
    error.value = typeof err === 'string' ? err : 'Failed to send password reset email'
  } finally {
    loading.value = false
  }
}

defineEmits(['switch-to-signup'])
</script>
