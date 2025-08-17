<template>
  <div class="text-center">
    <!-- Step Title -->
    <div class="text-h5 font-weight-bold mb-2 text-grey-darken-3">
      <v-icon icon="mdi-web" class="mr-2" color="primary"></v-icon>
      Portfolio Website
    </div>
    
    <!-- Step Description -->
    <div class="text-body-1 text-grey-darken-1 mb-6">
      Showcase your work and projects with a portfolio website link
    </div>

    <!-- Portfolio Section -->
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <div class="text-h6 mb-4">Do you have a portfolio website?</div>
      
      <!-- Portfolio Question -->
      <v-btn-toggle
        v-model="hasPortfolioSelection"
        color="primary"
        variant="outlined"
        divided
        mandatory
        class="mb-6"
      >
        <v-btn value="yes" size="large" class="px-8">
          <v-icon icon="mdi-check-circle-outline" class="mr-2"></v-icon>
          Yes, I have one
        </v-btn>
        <v-btn value="no" size="large" class="px-8">
          <v-icon icon="mdi-close-circle-outline" class="mr-2"></v-icon>
          No, I don't
        </v-btn>
      </v-btn-toggle>

      <!-- Portfolio URL Input -->
      <v-expand-transition>
        <div v-if="hasPortfolioSelection === 'yes'">
          <v-divider class="mb-6"></v-divider>
          
          <v-text-field
            v-model="portfolioUrl"
            label="Portfolio Website URL"
            variant="outlined"
            density="comfortable"
            prepend-inner-icon="mdi-web"
            placeholder="https://your-portfolio.com"
            :rules="portfolioRules"
            class="mb-4"
          >
            <template v-slot:append-inner>
              <v-tooltip text="Enter the full URL including https://">
                <template v-slot:activator="{ props }">
                  <v-icon
                    v-bind="props"
                    icon="mdi-help-circle-outline"
                    color="grey-darken-1"
                  ></v-icon>
                </template>
              </v-tooltip>
            </template>
          </v-text-field>

          <!-- Portfolio Examples -->
          <v-card variant="tonal" color="green-lighten-5" class="pa-4 mb-4">
            <div class="text-subtitle-2 font-weight-bold mb-2 text-green-darken-2">
              <v-icon icon="mdi-lightbulb-outline" class="mr-1"></v-icon>
              Popular portfolio platforms:
            </div>
            <div class="text-body-2 text-green-darken-1">
              <v-row>
                <v-col cols="12" md="6">
                  <ul class="pl-4">
                    <li>Personal website (yourname.com)</li>
                    <li>GitHub Pages</li>
                    <li>Netlify</li>
                    <li>Vercel</li>
                  </ul>
                </v-col>
                <v-col cols="12" md="6">
                  <ul class="pl-4">
                    <li>Portfolio.io</li>
                    <li>Behance</li>
                    <li>Dribbble</li>
                    <li>CodePen</li>
                  </ul>
                </v-col>
              </v-row>
            </div>
          </v-card>

          <!-- Validation Success -->
          <v-alert
            v-if="validationSuccess"
            type="success"
            variant="tonal"
            class="mb-4"
          >
            <div class="d-flex align-center">
              <v-icon icon="mdi-check-circle" class="mr-2"></v-icon>
              <div>
                <div class="font-weight-bold">Portfolio URL validated!</div>
                <div class="text-body-2">
                  Your portfolio website will be included in your resume.
                </div>
              </div>
            </div>
          </v-alert>
        </div>
      </v-expand-transition>

      <!-- No Portfolio Selected -->
      <v-expand-transition>
        <div v-if="hasPortfolioSelection === 'no'">
          <v-divider class="mb-6"></v-divider>
          
          <v-alert type="info" variant="tonal">
            <div class="d-flex align-center">
              <v-icon icon="mdi-information-outline" class="mr-2"></v-icon>
              <div>
                <div class="font-weight-bold">No worries!</div>
                <div class="text-body-2">
                  You can always add a portfolio website later in your profile settings.
                </div>
              </div>
            </div>
          </v-alert>
        </div>
      </v-expand-transition>

      <!-- Why Portfolio is Important -->
      <v-card variant="tonal" color="purple-lighten-5" class="pa-4 mt-4">
        <div class="text-subtitle-2 font-weight-bold mb-2 text-purple-darken-2">
          <v-icon icon="mdi-star-outline" class="mr-1"></v-icon>
          Why include a portfolio?
        </div>
        <div class="text-body-2 text-purple-darken-1">
          <ul class="pl-4">
            <li>Showcase your best work and projects</li>
            <li>Demonstrate your skills in action</li>
            <li>Stand out from other candidates</li>
            <li>Provide easy access to your work samples</li>
            <li>Show your personal brand and style</li>
          </ul>
        </div>
      </v-card>

      <!-- Skip Option -->
      <div class="text-center mt-4">
        <v-btn
          variant="text"
          color="grey-darken-1"
          @click="skipPortfolio"
          :disabled="onboarding.loading"
        >
          Skip this step
        </v-btn>
      </div>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useOnboardingStore } from '@/store/onboarding'

const onboarding = useOnboardingStore()

// Local state
const portfolioUrl = ref('')
const validationSuccess = ref(false)
const hasPortfolioSelection = ref<'yes' | 'no' | null>(null)

// Validation rules
const portfolioRules = [
  (v: string) => {
    if (!v) return true // Optional field
    try {
      new URL(v)
      return true
    } catch {
      return 'Please enter a valid URL (e.g., https://your-portfolio.com)'
    }
  }
]

// Watch for selection changes
watch(hasPortfolioSelection, (newValue) => {
  if (newValue === 'no') {
    portfolioUrl.value = ''
    onboarding.updateData({ portfolioUrl: '' })
    validationSuccess.value = false
  }
})

// Watch for URL changes
watch(portfolioUrl, (newValue) => {
  onboarding.updateData({ portfolioUrl: newValue })
  
  // Validate URL
  if (newValue && portfolioRules[0](newValue) === true) {
    validationSuccess.value = true
  } else {
    validationSuccess.value = false
  }
})

// Initialize from store
onMounted(() => {
  if (onboarding.data.portfolioUrl) {
    portfolioUrl.value = onboarding.data.portfolioUrl
    hasPortfolioSelection.value = 'yes'
  }
})

const skipPortfolio = () => {
  hasPortfolioSelection.value = 'no'
  portfolioUrl.value = ''
  onboarding.updateData({ portfolioUrl: '' })
  validationSuccess.value = false
}
</script>

<style scoped>
.v-btn-toggle {
  width: 100%;
}

.v-btn-toggle .v-btn {
  flex: 1;
}

ul li {
  margin-bottom: 4px;
}
</style>
