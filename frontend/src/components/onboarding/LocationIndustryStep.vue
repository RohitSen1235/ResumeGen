<template>
  <div class="text-center">
    <div class="text-h5 font-weight-bold mb-2 text-grey-darken-3">
      <v-icon icon="mdi-map-marker-outline" class="mr-2" color="primary"></v-icon>
      Tell us about your location and industry
    </div>
    <div class="text-body-1 text-grey-darken-1 mb-6">
      This helps us tailor your experience.
    </div>
    <v-card variant="outlined" class="pa-6 mb-6" rounded="lg">
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field
            v-model="city"
            label="City"
            variant="outlined"
            density="comfortable"
            placeholder="e.g., San Francisco"
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field
            v-model="country"
            label="Country"
            variant="outlined"
            density="comfortable"
            placeholder="e.g., USA"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-text-field
        v-model="industry"
        label="Industry"
        variant="outlined"
        density="comfortable"
        placeholder="e.g., Technology"
      ></v-text-field>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useOnboardingStore } from '@/store/onboarding'

const onboarding = useOnboardingStore()

const city = ref('')
const country = ref('')
const industry = ref('')

watch(city, (newValue) => {
  onboarding.updateData({ city: newValue })
})

watch(country, (newValue) => {
  onboarding.updateData({ country: newValue })
})

watch(industry, (newValue) => {
  onboarding.updateData({ industry: newValue })
})

onMounted(() => {
  city.value = onboarding.data.city
  country.value = onboarding.data.country
  industry.value = onboarding.data.industry
})
</script>
