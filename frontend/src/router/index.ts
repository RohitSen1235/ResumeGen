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

  // Check if route requires guest access
  if (to.meta.requiresGuest && auth.isAuthenticated) {
    return next('/resume-builder')
  }

  // Check if route requires authentication
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return next('/login')
  }

  // Check if route requires completed profile
  if (to.meta.requiresProfile && !auth.hasProfile) {
    return next('/profile')
  }

  next()
})

export default router
