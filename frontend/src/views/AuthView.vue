<template>
  <v-container class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-fade-transition mode="out-in">
          <login-form
            v-if="showLogin"
            @switch-to-signup="showLogin = false"
          />
          <signup-form
            v-else
            @switch-to-login="showLogin = true"
          />
        </v-fade-transition>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import LoginForm from '@/components/LoginForm.vue'
import SignupForm from '@/components/SignupForm.vue'

const showLogin = ref(true)
</script>
