<template>
  <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="500">
    <v-card-title class="text-h5 mb-4">
      <v-icon icon="mdi-login" size="large" class="mr-2" color="primary"></v-icon>
      Resume-Genie.ai Login
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

        <div class="text-center">
          Don't have an account?
          <a href="#" @click.prevent="$emit('switch-to-signup')" class="text-primary">
            Sign up
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

const email = ref('')
const password = ref('')
const isValid = ref(false)
const error = ref('')
const loading = ref(false)

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

defineEmits(['switch-to-signup'])
</script>
