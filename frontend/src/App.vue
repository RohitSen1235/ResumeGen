<template>
  <v-app>
    <!-- Navigation bar -->
    <v-app-bar
      color="primary"
      app
      elevation="4"
    >
      <v-app-bar-title class="text-h6">
        <router-link to="/" class="text-decoration-none text-white">
          ResumeBuilder.ai
        </router-link>
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <!-- Menu items for authenticated users -->
      <template v-if="auth.isAuthenticated">
        <v-btn
          :to="{ path: '/resume-builder' }"
          variant="text"
          class="mx-2 rounded-pill"
        >
          Resume Builder
        </v-btn>

        <v-btn
          :to="{ path: '/profile' }"
          variant="text"
          class="mx-2 rounded-pill"
        >
          Profile
        </v-btn>

        <v-btn
          @click="handleLogout"
          variant="text"
          class="mx-2 rounded-pill"
        >
          Logout
        </v-btn>
      </template>

      <!-- Menu items for unauthenticated users -->
      <template v-else>
        <v-btn
          :to="{ path: '/login' }"
          variant="text"
          class="mx-2 rounded-pill"
        >
          Login
        </v-btn>
        <v-btn
          :to="{ path: '/login' }"
          color="white"
          class="mx-2 rounded-pill"
        >
          Sign Up
        </v-btn>
      </template>
    </v-app-bar>

    <!-- Main content -->
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = () => {
  auth.logout()
  router.push('/')
}
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}

.v-btn {
  text-transform: none;
  letter-spacing: 0.5px;
}
</style>
