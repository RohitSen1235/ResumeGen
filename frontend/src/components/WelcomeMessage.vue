<template>
  <!-- Welcome Alert for authenticated users -->
  <v-alert
    v-if="showWelcome && auth.isAuthenticated"
    type="success"
    variant="tonal"
    closable
    @click:close="dismissWelcome"
    class="welcome-alert"
    :class="{ 'mobile-alert': mobile }"
  >
    <template v-slot:prepend>
      <v-icon icon="mdi-account-check"></v-icon>
    </template>
    
    <div class="d-flex align-center justify-space-between w-100">
      <div class="welcome-content">
        <div class="welcome-text text-h6 mb-1">
          {{ welcomeMessage }}
        </div>
        <div v-if="showTip && currentTip" class="welcome-tip text-body-2">
          {{ currentTip }}
        </div>
      </div>
      
      <div class="welcome-actions d-flex align-center ml-4" v-if="!mobile">
        <v-btn
          v-if="!auth.hasProfile"
          :to="{ path: '/profile' }"
          color="success"
          variant="outlined"
          size="small"
          class="mr-2"
          prepend-icon="mdi-account-plus"
        >
          Complete Profile
        </v-btn>
        <!-- <v-btn
          :to="{ path: '/resume-builder' }"
          color="success"
          variant="flat"
          size="small"
          prepend-icon="mdi-file-document-plus"
        >
          Create Resume
        </v-btn> -->
      </div>
    </div>
    
    <!-- Mobile actions -->
    <div v-if="mobile" class="welcome-actions-mobile mt-3">
      <v-btn
        v-if="!auth.hasProfile"
        :to="{ path: '/profile' }"
        color="success"
        variant="outlined"
        size="small"
        class="mr-2"
        prepend-icon="mdi-account-plus"
      >
        Complete Profile
      </v-btn>
      <!-- <v-btn
        :to="{ path: '/resume-builder' }"
        color="success"
        variant="flat"
        size="small"
        prepend-icon="mdi-file-document-plus"
      >
        Create Resume
      </v-btn> -->
    </div>
  </v-alert>

  <!-- Welcome Toast for mobile alternative -->
  <v-snackbar
    v-if="showMobileToast && mobile"
    v-model="showMobileToast"
    :timeout="6000"
    color="success"
    location="top"
    class="welcome-toast"
  >
    <div class="d-flex align-center">
      <v-icon icon="mdi-account-check" class="mr-2"></v-icon>
      <div>
        <div class="font-weight-medium">{{ welcomeMessage }}</div>
        <div v-if="showTip" class="text-caption">{{ currentTip }}</div>
      </div>
    </div>
    <template v-slot:actions>
      <v-btn
        color="white"
        variant="text"
        @click="showMobileToast = false"
        icon="mdi-close"
        size="small"
      ></v-btn>
    </template>
  </v-snackbar>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useDisplay } from 'vuetify'

const { mobile } = useDisplay()
const auth = useAuthStore()

const showWelcome = ref(false)
const showMobileToast = ref(false)
const showTip = ref(true)

// Welcome messages based on different scenarios
const welcomeMessage = computed(() => {
  const user = auth.user
  if (!user) return 'Welcome to ResumeGen!'

  const name = user.profile?.name || user.email?.split('@')[0] || 'there'
  const timeOfDay = getTimeOfDay()
  
  // Different messages based on user state
  if (isNewUser.value) {
    return `Welcome to ResumeGenie, ${name}! 🎉`
  } else if (isReturningUser.value) {
    return `Welcome back, ${name}! ${timeOfDay} ☀️`
  } else {
    return `${timeOfDay}, ${name}! Ready to build your perfect resume?`
  }
})

// Tips based on user profile completion and usage
const currentTip = computed(() => {
  if (!auth.user) return 'Start building your professional resume today!'
  
  if (!auth.hasProfile) {
    return 'Complete your profile to get personalized resume suggestions.'
  } else if (auth.user.credits === 0) {
    return 'Get more credits to unlock premium features and templates.'
  } else if (auth.user.credits > 0) {
    return `You have ${auth.user.credits} credits available for premium features.`
  } else {
    return 'Explore our AI-powered resume builder to create your perfect resume.'
  }
})

// Check if user is new (created within last 24 hours)
const isNewUser = computed(() => {
  if (!auth.user?.created_at) return true // Default to new user if no creation date
  try {
    const createdAt = new Date(auth.user.created_at)
    const now = new Date()
    const hoursDiff = (now.getTime() - createdAt.getTime()) / (1000 * 60 * 60)
    return hoursDiff < 24
  } catch (error) {
    return true
  }
})

// Check if user is returning (last login was more than 1 day ago)
const isReturningUser = computed(() => {
  const lastWelcome = localStorage.getItem('lastWelcomeShown')
  if (!lastWelcome) return false
  
  try {
    const lastShown = new Date(lastWelcome)
    const now = new Date()
    const hoursDiff = (now.getTime() - lastShown.getTime()) / (1000 * 60 * 60)
    return hoursDiff > 24
  } catch (error) {
    return false
  }
})

// Get appropriate greeting based on time of day
const getTimeOfDay = () => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

// Show welcome message when user logs in
const showWelcomeMessage = () => {
  if (!auth.isAuthenticated) return
  
  // For testing purposes - always show welcome message
  // TODO: Remove this and uncomment the logic below for production
  displayWelcome()
  return
  
  // Production logic (commented out for testing)
  /*
  const lastWelcome = localStorage.getItem('lastWelcomeShown')
  const now = new Date()
  
  if (!lastWelcome) {
    displayWelcome()
    return
  }
  
  try {
    const lastShown = new Date(lastWelcome)
    const hoursDiff = (now.getTime() - lastShown.getTime()) / (1000 * 60 * 60)
    
    if (hoursDiff > 1 || isNewUser.value) {
      displayWelcome()
    }
  } catch (error) {
    displayWelcome()
  }
  */
}

const displayWelcome = () => {
  console.log('Displaying welcome message:', welcomeMessage.value) // Debug log
  
  if (mobile.value) {
    showMobileToast.value = true
  } else {
    showWelcome.value = true
  }
  
  // Store timestamp
  localStorage.setItem('lastWelcomeShown', new Date().toISOString())
  
  // Auto-hide alert after 10 seconds on desktop
  if (!mobile.value) {
    setTimeout(() => {
      showWelcome.value = false
    }, 10000)
  }
}

const dismissWelcome = () => {
  showWelcome.value = false
  localStorage.setItem('lastWelcomeShown', new Date().toISOString())
}

// Watch for authentication changes
watch(() => auth.isAuthenticated, (newVal) => {
  console.log('Auth state changed:', newVal) // Debug log
  if (newVal) {
    // Small delay to ensure user data is loaded
    setTimeout(() => {
      showWelcomeMessage()
    }, 500)
  } else {
    showWelcome.value = false
    showMobileToast.value = false
  }
})

// Show welcome on mount if user is already authenticated
onMounted(() => {
  console.log('Component mounted, auth state:', auth.isAuthenticated, 'user:', auth.user) // Debug log
  if (auth.isAuthenticated && auth.user) {
    setTimeout(() => {
      showWelcomeMessage()
    }, 1000)
  }
})
</script>

<style scoped>
.welcome-alert {
  position: fixed;
  top: 64px;
  left: 16px;
  right: 16px;
  z-index: 1000;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideDown 0.3s ease-out;
}

.mobile-alert {
  top: 56px;
  left: 8px;
  right: 8px;
}

.welcome-content {
  flex: 1;
  min-width: 0;
}

.welcome-text {
  font-weight: 600;
  color: #1b5e20;
}

.welcome-tip {
  color: #2e7d32;
  font-weight: 400;
}

.welcome-actions {
  flex-shrink: 0;
}

.welcome-actions-mobile {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.welcome-toast {
  margin-top: 56px;
}

/* Mobile responsiveness */
@media (max-width: 960px) {
  .welcome-alert {
    top: 56px;
  }
  
  .welcome-text {
    font-size: 1rem;
  }
  
  .welcome-tip {
    font-size: 0.875rem;
  }
}

@media (max-width: 600px) {
  .welcome-alert {
    left: 4px;
    right: 4px;
    top: 56px;
  }
  
  .welcome-text {
    font-size: 0.9rem;
  }
  
  .welcome-tip {
    font-size: 0.8rem;
  }
  
  .welcome-actions-mobile .v-btn {
    font-size: 0.75rem;
    height: 32px;
  }
}

/* Animation for smooth appearance */
@keyframes slideDown {
  from {
    transform: translateY(-100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Ensure alert doesn't interfere with page content */
.welcome-alert + * {
  margin-top: 0;
}
</style>
