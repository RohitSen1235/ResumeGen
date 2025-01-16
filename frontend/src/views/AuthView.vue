<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6">
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

const route = useRoute()
const formType = computed(() => route.meta.formType)
</script>
