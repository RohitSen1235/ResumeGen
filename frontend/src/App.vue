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
          <!-- Credits display -->
          <v-chip
            color="orange-lighten-2"
            variant="outlined"
            class="mr-3"
            prepend-icon="mdi-coin"
          >
            {{ auth.user?.credits || 0 }} Credits
          </v-chip>

          <v-btn
            :to="{ path: '/pricing' }"
            variant="text"
            color="orange-lighten-2"
            class="text-none"
          >
            Pricing
          </v-btn>

          <v-btn
            :to="{ path: '/resume-builder' }"
            variant="text"
            color="orange-lighten-2"
            class="text-none"
          >
            Resume Builder
          </v-btn>

          <v-btn
            :to="{ path: '/profile' }"
            variant="text"
            color="orange-lighten-2"
            class="text-none"
          >
            Profile
          </v-btn>

          <v-btn
            v-if="auth.user?.is_admin"
            :to="{ path: '/admin' }"
            variant="text"
            color="orange-lighten-2"
            class="text-none"
          >
            Admin
          </v-btn>

          <v-btn
            @click="handleLogout"
            variant="text"
            color="orange-lighten-2"
            class="text-none"
          >
            Logout
          </v-btn>
        </template>
        <template v-else>
          <v-btn
            :to="{ path: '/pricing' }"
            variant="text"
            color="orange-lighten-2"
            class="text-none"
          >
            Pricing
          </v-btn>
          <v-btn
            :to="{ path: '/login' }"
            variant="text"
            color="orange-lighten-2"
            class="text-none"
          >
            Login
          </v-btn>
          <v-btn
            :to="{ path: '/signup' }"
            variant="outlined"
            color="orange-lighten-2"
            class="text-none ml-2 mr-4"
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
          <!-- Credits display for mobile -->
          <v-list-item>
            <v-chip
              color="orange-lighten-2"
              variant="outlined"
              prepend-icon="mdi-coin"
              class="ma-2"
            >
              {{ auth.user?.credits || 0 }} Credits
            </v-chip>
          </v-list-item>
          
          <v-list-item
            :to="{ path: '/pricing' }"
            title="Pricing"
          ></v-list-item>
          <v-list-item
            :to="{ path: '/resume-builder' }"
            title="Resume Builder"
          ></v-list-item>
          <v-list-item
            :to="{ path: '/profile' }"
            title="Profile"
          ></v-list-item>
          <v-list-item
            v-if="auth.user?.is_admin"
            :to="{ path: '/admin' }"
            title="Admin"
          ></v-list-item>
          <v-list-item
            @click="handleLogout"
            title="Logout"
          ></v-list-item>
        </template>
        <template v-else>
          <v-list-item
            :to="{ path: '/pricing' }"
            title="Pricing"
          ></v-list-item>
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

    <!-- Welcome Message Component -->
    <WelcomeMessage />

    <!-- Main content -->
    <v-main>
      <router-view></router-view>
    </v-main>

    <!-- Footer -->
    <v-footer class="footer-section" color="#0D47A1">
      <v-container class="py-8">
        <!-- Main Footer Content -->
        <v-row class="mb-6">
          <!-- Brand Section -->
          <v-col cols="12" md="4" class="mb-4">
            <div class="d-flex align-center mb-3">
              <img 
                src="./assets/logo.svg" 
                alt="Resume Genie" 
                class="footer-logo mr-3"
              >
              <h3 class="text-white font-weight-bold">Resume Genie</h3>
            </div>
            <p class="text-grey-lighten-1 mb-3">
              Create professional resumes with AI-powered assistance. 
              Land your dream job with our intelligent resume builder.
            </p>
            <div class="d-flex">
              <v-btn
                icon
                variant="text"
                color="white"
                size="small"
                class="mr-2"
              >
                <v-icon>mdi-twitter</v-icon>
              </v-btn>
              <v-btn
                icon
                variant="text"
                color="white"
                size="small"
                class="mr-2"
              >
                <v-icon>mdi-linkedin</v-icon>
              </v-btn>
              <v-btn
                icon
                variant="text"
                color="white"
                size="small"
              >
                <v-icon>mdi-github</v-icon>
              </v-btn>
            </div>
          </v-col>

          <!-- Quick Links -->
          <v-col cols="12" sm="6" md="2" class="mb-4">
            <h4 class="text-white font-weight-medium mb-3">Quick Links</h4>
            <div class="footer-links">
              <v-btn 
                to="/pricing" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                Pricing
              </v-btn>
              <v-btn 
                to="/resume-builder" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                Resume Builder
              </v-btn>
              <v-btn 
                to="/blog" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                Blog
              </v-btn>
            </div>
          </v-col>

          <!-- Support -->
          <v-col cols="12" sm="6" md="2" class="mb-4">
            <h4 class="text-white font-weight-medium mb-3">Support</h4>
            <div class="footer-links">
              <v-btn 
                to="/faq" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                FAQ
              </v-btn>
              <v-btn 
                to="/about-us" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                About Us
              </v-btn>
              <v-btn 
                href="mailto:support@resumegenie.com" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                Contact
              </v-btn>
            </div>
          </v-col>

          <!-- Legal -->
          <v-col cols="12" sm="6" md="2" class="mb-4">
            <h4 class="text-white font-weight-medium mb-3">Legal</h4>
            <div class="footer-links">
              <v-btn 
                to="/privacy-policy" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                Privacy Policy
              </v-btn>
              <v-btn 
                to="/terms-of-service" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                Terms of Service
              </v-btn>
              <v-btn 
                to="/user-agreement" 
                variant="text" 
                color="grey-lighten-1"
                class="footer-link pa-0 justify-start"
                block
              >
                User Agreement
              </v-btn>
            </div>
          </v-col>

          <!-- Newsletter -->
          <v-col cols="12" md="2" class="mb-4">
            <h4 class="text-white font-weight-medium mb-3">Stay Updated</h4>
            <p class="text-grey-lighten-1 text-caption mb-3">
              Get tips and updates delivered to your inbox
            </p>
            <v-text-field
              placeholder="Enter email"
              variant="outlined"
              density="compact"
              color="white"
              bg-color="rgba(255,255,255,0.1)"
              class="mb-2"
              hide-details
            ></v-text-field>
            <v-btn
              color="orange-lighten-2"
              variant="flat"
              size="small"
              block
              class="text-none"
            >
              Subscribe
            </v-btn>
          </v-col>
        </v-row>

        <!-- Bottom Bar -->
        <v-divider color="rgba(255,255,255,0.2)" class="mb-4"></v-divider>
        <v-row align="center">
          <v-col cols="12" md="6">
            <p class="text-grey-lighten-1 text-caption mb-0">
              © {{ new Date().getFullYear() }} Resume Genie. All rights reserved.
            </p>
          </v-col>
          <v-col cols="12" md="6" class="text-md-right">
            <p class="text-grey-lighten-1 text-caption mb-0">
              Made with ❤️ for job seekers worldwide
            </p>
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/store/auth'
import { useRouter } from 'vue-router'
import { ref, computed } from 'vue'
import { useDisplay } from 'vuetify'
import WelcomeMessage from '@/components/WelcomeMessage.vue'

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
  .v-app { /* Apply flex properties to v-app */
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  .v-main { /* Ensure v-main grows */
    flex-grow: 1;
  }
  .v-footer {
    position: relative !important;
    bottom: auto !important;
  }
  /* Styles for footer content to prevent overlap */
  .v-footer .v-container .v-row[justify="center"] {
    flex-wrap: wrap; /* Allow columns to wrap */
  }
  .v-footer .v-container .v-col[cols="12"][md="auto"] {
    flex-basis: 150px; /* Try to fit columns horizontally */
    flex-grow: 0; /* Prevent columns from growing beyond their basis */
    margin: 5px; /* Add some margin between columns */
  }
}

@media (max-width: 600px) {
  .v-app-bar-title {
    font-size: 1rem !important;
  }
}

/* Footer Styles */
.footer-section {
  margin-top: auto;
}

.footer-logo {
  height: 40px;
  width: auto;
}

.footer-links {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-link {
  text-align: left !important;
  font-size: 0.875rem !important;
  font-weight: 400 !important;
  min-height: 32px !important;
  transition: color 0.2s ease;
}

.footer-link:hover {
  color: white !important;
}

/* Mobile Footer Adjustments */
@media (max-width: 960px) {
  .footer-section .v-container {
    padding-top: 32px !important;
    padding-bottom: 32px !important;
  }
  
  .footer-section h4 {
    font-size: 1.1rem !important;
    margin-bottom: 16px !important;
  }
  
  .footer-section .v-col {
    margin-bottom: 24px !important;
  }
  
  .footer-logo {
    height: 32px;
  }
  
  .footer-links {
    gap: 4px;
  }
  
  .footer-link {
    font-size: 0.8rem !important;
    min-height: 28px !important;
  }
}

@media (max-width: 600px) {
  .footer-section .v-container {
    padding-top: 24px !important;
    padding-bottom: 24px !important;
  }
  
  .footer-section h3 {
    font-size: 1.25rem !important;
  }
  
  .footer-section h4 {
    font-size: 1rem !important;
    margin-bottom: 12px !important;
  }
  
  .footer-section p {
    font-size: 0.875rem !important;
    line-height: 1.4 !important;
  }
  
  .footer-section .text-caption {
    font-size: 0.75rem !important;
  }
  
  .footer-section .v-col {
    margin-bottom: 20px !important;
  }
  
  .footer-logo {
    height: 28px;
  }
}

/* Newsletter Input Styling */
.footer-section .v-text-field .v-field {
  border-radius: 8px;
}

.footer-section .v-text-field .v-field__input {
  color: white;
}

.footer-section .v-text-field .v-field__input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

/* Social Media Icons */
.footer-section .v-btn--icon {
  border-radius: 50%;
  transition: all 0.2s ease;
}

.footer-section .v-btn--icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

/* Divider Styling */
.footer-section .v-divider {
  opacity: 0.3;
}

/* Bottom Bar Text */
.footer-section .text-md-right {
  text-align: right;
}

@media (max-width: 960px) {
  .footer-section .text-md-right {
    text-align: left;
  }
}
</style>
