<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-fade-transition mode="out-in">
          <login-form
            v-if="isLogin"
            @switch-to-signup="$router.push('/signup')"
          />
          <signup-form
            v-else
            @switch-to-login="$router.push('/login')"
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

const route = useRoute()
const isLogin = computed(() => route.meta.formType === 'login')
</script>
