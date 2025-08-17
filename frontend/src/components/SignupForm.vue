<template>
  <div>
    <div class="text-h5 text-center font-weight-medium mb-6">Create Your Account</div>
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
        :rules="[v => !!v || 'Password is required', v => v.length >= 8 || 'Password must be at least 8 characters']"
        variant="outlined"
        density="comfortable"
        prepend-inner-icon="mdi-lock-outline"
        class="mb-4"
      ></v-text-field>

      <v-text-field
        v-model="confirmPassword"
        label="Confirm Password"
        type="password"
        :rules="[v => !!v || 'Please confirm your password', v => v === password || 'Passwords must match']"
        variant="outlined"
        density="comfortable"
        prepend-inner-icon="mdi-lock-check-outline"
        class="mb-4"
      ></v-text-field>

      <v-checkbox
        v-model="userAgreement"
        :rules="[v => !!v || 'You must agree to the terms to continue']"
        required
        density="comfortable"
        class="mb-2"
      >
        <template v-slot:label>
          <div class="text-body-2">
            I agree to the 
            <router-link to="/user-agreement" target="_blank" class="text-primary text-decoration-none">
              User Agreement
            </router-link>, 
            <router-link to="/terms-of-service" target="_blank" class="text-primary text-decoration-none">
              Terms of Service
            </router-link>, and 
            <router-link to="/privacy-policy" target="_blank" class="text-primary text-decoration-none">
              Privacy Policy
            </router-link>
          </div>
        </template>
      </v-checkbox>

      <v-alert v-if="error" type="error" variant="tonal" class="mb-4" closable>
        {{ error }}
      </v-alert>

      <div class="d-flex justify-center">
        <v-btn
          type="submit"
          color="orange-lighten-2"
          :loading="loading"
          :disabled="!isValid"
          size="large"
          class="elevation-4 mx-auto"
          rounded="lg"
          width="300"
        >
          Sign Up
        </v-btn>
      </div>

      <v-divider class="my-4">
        <span class="text-overline text-grey-darken-1">OR</span>
      </v-divider>

      <div class="d-flex justify-center">
        <linked-in-button />
      </div>

      <div class="text-center mt-4">
        <a href="#" @click.prevent="$emit('switch-to-login')" class="text-primary text-body-2">
          Already have an account? Login
        </a>
      </div>
    </v-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LinkedInButton from './LinkedInButton.vue'
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const userAgreement = ref(false)
const isValid = ref(false)
const error = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  if (!isValid.value) return

  try {
    loading.value = true
    await auth.signup(email.value, password.value)
    router.push('/onboarding')
  } catch (err: any) {
    error.value = err.toString()
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

defineEmits(['switch-to-login'])
</script>
