<template>
  <v-card class="mx-auto pa-6" elevation="8" rounded="lg" max-width="500">
    <v-card-title class="d-flex align-center justify-center flex-column mb-4">
      <img src="@/assets/logo-dark.svg" alt="Resume Genie Logo" class="mb-4" style="width: 300px; height: auto;">
      <div class="text-h5">Sign Up</div>
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
        :rules="[
          v => !!v || 'Password is required',
          v => v.length >= 8 || 'Password must be at least 8 characters'
        ]"
        variant="outlined"
        density="comfortable"
        class="mb-4"
      ></v-text-field>

      <v-text-field
        v-model="confirmPassword"
        label="Confirm Password"
        type="password"
        :rules="[
          v => !!v || 'Please confirm your password',
          v => v === password || 'Passwords must match'
        ]"
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
          Sign Up
        </v-btn>

        <div class="text-center">
          Already have an account?
          <a href="#" @click.prevent="$emit('switch-to-login')" class="text-primary">
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

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const isValid = ref(false)
const error = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    await auth.signup(email.value, password.value)
    router.push('/profile')
  } catch (err: any) {
    error.value = err.toString()
  } finally {
    loading.value = false
  }
}

defineEmits(['switch-to-login'])
</script>
