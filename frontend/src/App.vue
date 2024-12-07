<template>
  <v-app>
    <!-- Navigation bar for authenticated users -->
    <v-app-bar
      v-if="auth.isAuthenticated"
      color="primary"
      app
      elevation="4"
    >
      <v-app-bar-title class="text-h6">
        Resume Builder
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <v-btn
        :to="{ path: '/resume-builder' }"
        variant="text"
        class="mx-2"
      >
        Resume Builder
      </v-btn>

      <v-btn
        :to="{ path: '/profile' }"
        variant="text"
        class="mx-2"
      >
        Profile
      </v-btn>

      <v-btn
        @click="handleLogout"
        variant="text"
        class="mx-2"
      >
        Logout
      </v-btn>
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
  router.push('/login')
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
