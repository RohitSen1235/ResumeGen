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
      path: '/pricing',
      name: 'Pricing',
      component: () => import('@/views/PricingView.vue')
    },
    {
      path: '/checkout',
      name: 'Checkout',
      component: () => import('@/views/CheckoutView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/payment/callback',
      name: 'PaymentCallback',
      component: () => import('@/views/PaymentCallbackView.vue'),
      meta: { requiresAuth: true }
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
      path: '/auth/linkedin/callback',
      component: () => import('@/views/LinkedInCallback.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/onboarding',
      component: () => import('@/views/OnboardingView.vue'),
      meta: { requiresAuth: true, requiresIncompleteOnboarding: true }
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
      path: '/review-download',
      component: () => import('@/views/ReviewAndDownloadView.vue'),
      meta: { requiresAuth: true, requiresProfile: true }
    },
    {
      path: '/resume/:id',
      component: () => import('@/views/ResumeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      component: () => import('@/views/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/users',
      component: () => import('@/components/admin/UserManagement.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/templates',
      component: () => import('@/components/admin/TemplateManagement.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/admin/staging-templates',
      component: () => import('@/views/admin/StagingTemplateManagement.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/privacy-policy',
      component: () => import('@/views/PrivacyPolicyView.vue')
    },
    {
      path: '/user-agreement',
      component: () => import('@/views/UserAgreementView.vue')
    },
    {
      path: '/about-us',
      component: () => import('@/views/AboutUsView.vue')
    },
    {
      path: '/faq',
      component: () => import('@/views/FAQView.vue')
    },
    {
      path: '/terms-of-service',
      component: () => import('@/views/TermsOfServiceView.vue')
    },
    {
      path: '/blog',
      component: () => import('@/views/BlogView.vue')
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

  // Check if route requires admin access
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return next('/')
  }

  // Check if route requires guest access
  if (to.meta.requiresGuest && auth.isAuthenticated) {
    // For authenticated users, check onboarding status first
    try {
      await auth.fetchUser()
      if (!auth.hasCompletedOnboarding) {
        return next('/onboarding')
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error)
    }
    return next('/resume-builder')
  }

  // PRIORITY CHECK: Always check onboarding completion first for authenticated users
  if (to.meta.requiresAuth && to.path !== '/onboarding') {
    try {
      await auth.fetchUser()
      if (!auth.hasCompletedOnboarding) {
        return next('/onboarding')
      }
    } catch (error) {
      console.error('Failed to fetch user data:', error)
    }
  }

  // Check if route requires completed profile
  if (to.meta.requiresProfile) {
    try {
      // Ensure profile data is fresh
      await auth.fetchUser()
      if (!auth.hasProfile) {
        return next('/onboarding')
      }
      // Onboarding completion is already checked above
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      // Continue to route even if profile fetch fails
    }
  }

  // Check if route requires incomplete onboarding (onboarding flow)
  if (to.meta.requiresIncompleteOnboarding) {
    try {
      // Ensure profile data is fresh
      await auth.fetchUser()
      if (auth.hasCompletedOnboarding) {
        return next('/resume-builder')
      }
    } catch (error) {
      console.error('Failed to fetch profile:', error)
      // Continue to route even if profile fetch fails
    }
  }

  next()
})

export default router
