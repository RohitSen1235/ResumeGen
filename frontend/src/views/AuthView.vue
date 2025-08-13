<template>
  <v-container class="fill-height pa-0" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" md="10" lg="8">
        <v-card class="elevation-12 rounded-xl" style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.8);">
          <v-row no-gutters>
            <v-col cols="12" md="6" class="d-flex flex-column justify-center pa-8">
              <div class="text-center mb-8">
                <h1 class="text-h4 font-weight-bold mb-4 text-grey-darken-3">Build Your Perfect Resume</h1>
                <p class="text-body-1 text-grey-darken-1">
                  Join thousands of professionals who landed their dream jobs with our AI-powered resume builder.
                </p>
              </div>
              <v-fade-transition mode="out-in">
                <login-form v-if="formType === 'login'" @switch-to-signup="$router.push('/signup')" />
                <signup-form v-else-if="formType === 'signup'" @switch-to-login="$router.push('/login')" />
                <forgot-password v-else-if="formType === 'forgot-password'" />
                <reset-password v-else-if="formType === 'reset-password'" />
              </v-fade-transition>
            </v-col>
            <v-col cols="12" md="6" class="d-none d-md-flex align-center justify-center pa-8" style="background-color: rgba(255, 255, 255, 0.5);">
              <div class="text-center">
                <img src="@/assets/logo-dark.svg" alt="Resume Genie" style="width: 250px; height: auto;" class="mb-6">
                <p class="text-h6 font-weight-medium text-grey-darken-2 mb-4">Quick Sign-in</p>
                <linked-in-button />
              </div>
            </v-col>
          </v-row>
        </v-card>
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
