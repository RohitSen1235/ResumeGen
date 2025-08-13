<template>
  <div>
    <div class="text-h5 text-center font-weight-medium mb-6">Login to Your Account</div>
    <v-form @submit.prevent="handleSubmit" v-model="isValid">
      <v-text-field
        v-model="email"
        label="Email"
        type="email"
        :rules="[v => !!v || 'Email is required', v => /.+@.+\..+/.test(v) || 'Email must be valid']"
        variant="outlined"
        density="comfortable"
        prepend-inner-icon="mdi-email-outline"
        class="mb-4"
      ></v-text-field>

      <v-text-field
        v-model="password"
        label="Password"
        type="password"
        :rules="[v => !!v || 'Password is required']"
        variant="outlined"
        density="comfortable"
        prepend-inner-icon="mdi-lock-outline"
        class="mb-4"
      ></v-text-field>

      <v-checkbox
        v-model="userAgreement"
        :rules="[v => !!v || 'You must agree to the terms to continue']"
        label="I agree to the terms and conditions"
        required
        density="comfortable"
      ></v-checkbox>

      <v-alert v-if="error" type="error" variant="tonal" class="mb-4" closable>
        {{ error }}
      </v-alert>

      <v-btn
        type="submit"
        color="primary"
        block
        :loading="loading"
        :disabled="!isValid"
        size="large"
        class="elevation-4"
        rounded="lg"
      >
        Login
      </v-btn>

      <div class="d-flex justify-space-between align-center mt-4">
        <a href="/forgot-password" class="text-primary text-body-2">Forgot password?</a>
        <a href="/signup" class="text-primary text-body-2">
          Don't have an account? Sign up
        </a>
      </div>
    </v-form>
  </div>
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
const userAgreement = ref<boolean>(false)
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
