<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6">
        <div class="text-center mb-8">
          <h1 class="text-h4 mb-2">Build Your Perfect Resume</h1>
          <p class="text-body-1">
            Join thousands of professionals who landed their dream jobs with our AI-powered resume builder.
            Get started in seconds!
          </p>
        </div>

        <v-card class="mb-6" variant="outlined">
          <v-card-text class="text-center pa-4">
            <p class="text-body-1 mb-2">Quick sign in with</p>
            <linked-in-button />
          </v-card-text>
          <v-divider></v-divider>
          <v-card-text class="text-center text-medium-emphasis">
            Or continue with email
          </v-card-text>
        </v-card>

        <v-fade-transition mode="out-in">
          <login-form
            v-if="formType === 'login'"
            @switch-to-signup="$router.push('/signup')"
          />
          <signup-form
            v-else-if="formType === 'signup'"
            @switch-to-login="$router.push('/login')"
          />
          <forgot-password
            v-else-if="formType === 'forgot-password'"
          />
          <reset-password
            v-else-if="formType === 'reset-password'"
          />
        </v-fade-transition>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import LoginForm from '@/components/LoginForm.vue'
import SignupForm from '@/components/SignupForm.vue'
import ForgotPassword from '@/components/ForgotPassword.vue'
import ResetPassword from '@/components/ResetPassword.vue'
import LinkedInButton from '@/components/LinkedInButton.vue'

const route = useRoute()
const formType = computed(() => route.meta.formType)
</script>
