import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { watch } from 'vue'

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
      meta: { requiresGuest: true, formType: 'login' }
    },
    {
      path: '/signup',
      component: () => import('@/views/AuthView.vue'),
      meta: { requiresGuest: true, formType: 'signup' }
    },
    {
      path: '/forgot-password',
      component: () => import('@/views/AuthView.vue'),
      meta: { requiresGuest: true, formType: 'forgot-password' }
    },
    {
      path: '/reset-password',
      component: () => import('@/views/AuthView.vue'),
      meta: { requiresGuest: true, formType: 'reset-password' }
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
    },
    {
      path: '/resume/:id',
      component: () => import('@/views/ResumeView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  // Skip auth checks for public routes
  if (!to.meta.requiresAuth && !to.meta.requiresProfile) {
    return next()
  }

  // If no token, redirect to login
  if (!auth.token) {
    return next('/login')
  }

  // Wait for initial auth validation to complete
  if (auth.initializing) {
    try {
      await new Promise(resolve => {
        const unwatch = watch(() => auth.initializing, (val) => {
          if (!val) {
            unwatch()
            resolve(null)
          }
        })
      })
    } catch {
      return next('/login')
    }
  }

  // Validate token for protected routes
  if (to.meta.requiresAuth || to.meta.requiresProfile) {
    const isValid = await auth.validateToken()
    if (!isValid) {
      auth.logout()
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
