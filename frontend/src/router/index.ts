import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/views/HomeView.vue')
    },
    {
      path: '/login',
      component: () => import('@/views/AuthView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/profile',
      component: () => import('@/components/ProfileForm.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/resume-builder',
      component: () => import('@/components/ResumeBuilder.vue'),
      meta: { requiresAuth: true, requiresProfile: true }
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Only validate token if navigating to a protected route
  if (to.meta.requiresAuth || to.meta.requiresProfile) {
    if (auth.token) {
      const isValid = await auth.validateToken()
      if (!isValid) {
        auth.logout()
        return next('/login')
      }
    } else {
      return next('/login')
    }
  }

  // Check if route requires guest access
  if (to.meta.requiresGuest && auth.isAuthenticated) {
    return next('/resume-builder')
  }

  // Check if route requires completed profile
  if (to.meta.requiresProfile) {
    try {
      // Ensure profile data is fresh
      await auth.fetchUser()
      if (!auth.hasProfile) {
        return next('/profile')
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      // Continue to route even if profile fetch fails
    }
  }

  next()
})

export default router
