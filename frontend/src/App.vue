<template>
  <v-app>
    <!-- Navigation bar -->
    <v-app-bar
      color="#1565C0"
      app
      elevation="4"
    >
      <v-app-bar-nav-icon
        @click="drawer = !drawer"
        class="d-md-none"
      ></v-app-bar-nav-icon>
      
      <v-app-bar-title class="text-h6">
        <router-link to="/" class="text-decoration-none text-white">
          <img 
            src="./assets/logo.svg" 
            alt="Resume Genie" 
            class="logo" 
            :style="{
              height: mobile ? '36px' : '48px',
              marginRight: '8px'
            }"
          >
        </router-link>
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <!-- Desktop menu -->
      <div class="d-none d-md-flex">
        <!-- Menu items for authenticated users -->
        <template v-if="auth.isAuthenticated">
          <v-btn
            :to="{ path: '/resume-builder' }"
            variant="text"
            class="mx-1 rounded-pill"
            size="small"
          >
            Resume Builder
          </v-btn>

          <v-btn
            :to="{ path: '/profile' }"
            variant="text"
            class="mx-1 rounded-pill"
            size="small"
          >
            Profile
          </v-btn>

          <v-btn
            @click="handleLogout"
            variant="text"
            class="mx-1 rounded-pill"
            size="small"
          >
            Logout
          </v-btn>
        </template>

        <!-- Menu items for unauthenticated users -->
        <template v-else>
          <v-btn
            :to="{ path: '/login' }"
            variant="text"
            class="mx-1 rounded-pill"
            size="small"
          >
            Login
          </v-btn>
          <v-btn
            :to="{ path: '/signup' }"
            color="white"
            class="mx-1 rounded-pill"
            size="small"
          >
            Sign Up
          </v-btn>
        </template>
      </div>
    </v-app-bar>

    <!-- Mobile navigation drawer -->
    <v-navigation-drawer
      v-model="drawer"
      temporary
      location="left"
      class="d-md-none"
    >
      <v-list>
        <template v-if="auth.isAuthenticated">
          <v-list-item
            :to="{ path: '/resume-builder' }"
            title="Resume Builder"
          ></v-list-item>
          <v-list-item
            :to="{ path: '/profile' }"
            title="Profile"
          ></v-list-item>
          <v-list-item
            @click="handleLogout"
            title="Logout"
          ></v-list-item>
        </template>
        <template v-else>
          <v-list-item
            :to="{ path: '/login' }"
            title="Login"
          ></v-list-item>
          <v-list-item
            :to="{ path: '/signup' }"
            title="Sign Up"
          ></v-list-item>
        </template>
      </v-list>
    </v-navigation-drawer>

    <!-- Main content -->
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'
import { useDisplay } from 'vuetify'

const { mobile } = useDisplay()
const auth = useAuthStore()
const router = useRouter()
const drawer = ref(false)

const handleLogout = () => {
  auth.logout()
  router.push('/')
  drawer.value = false
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

.logo {
  transition: transform 0.2s ease;
}

.logo:hover {
  transform: scale(1.05);
}

@media (max-width: 960px) {
  .v-toolbar__content {
    padding: 0 12px !important;
  }
  
  .v-btn {
    font-size: 0.8rem !important;
    min-width: auto !important;
    padding: 0 8px !important;
  }
}

@media (max-width: 600px) {
  .v-app-bar-title {
    font-size: 1rem !important;
  }
}
</style>
