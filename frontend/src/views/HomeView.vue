<template>
  <v-container fluid class="pa-0">
    <!-- Hero Section -->
    <v-row class="bg-primary hero-section" style="min-height: 80vh">
      <v-container>
        <v-row align="center" style="min-height: 80vh">
          <v-col cols="12" md="6">
            <h1 class="text-h2 font-weight-bold mb-4 text-white">
              Job-Optimized Resumes in Minutes
            </h1>
            <p class="text-h6 mb-6 text-white">
              AI-powered customization for each application in 
            </p>
            <div class="timer-comparison mb-6">
              <v-chip color="green" class="text-grey-1 mr-2">5 min</v-chip>
              <span class="text-white">vs</span>
              <v-chip color="red-lighten-1" class="text-grey-1 ml-2">60 min</v-chip>
              <span class="text-white ml-2">manual editing</span>
            </div>
            <div class="d-flex gap-4">
              <v-btn
                :to="{ path: '/login' }"
                size="x-large"
                color="orange-lighten-2"
                class="text-grey-darken-4 rounded-pill px-8"
                elevation="4"
              >
                Get Started
              </v-btn>
              <!-- <v-btn
                href="/auth/linkedin"
                size="x-large"
                color="orange-lighten-2"
                class="text-grey-darken-4 rounded-pill px-8"
                elevation="4"
              >
                <v-img
                  src="@/assets/Sign-In-Large---Active.png"
                  max-height="24"
                  max-width="24"
                  class="mr-2"
                ></v-img>
                Continue with LinkedIn
              </v-btn> -->
            </div>
          </v-col>
          <v-col cols="12" md="6" class="d-flex justify-center">
            <v-img
              src="/resume-preview.png"
              max-width="500"
              class="elevation-10 rounded"
            ></v-img>
          </v-col>
        </v-row>
      </v-container>
    </v-row>

    <!-- Value Propositions Section -->
    <v-container class="py-16 value-props-section">
      <v-row>
        <v-col cols="12" class="text-center mb-12">
          <h2 class="text-h3 font-weight-bold mb-3">Optimized for Success</h2>
          <p class="text-h6 text-medium-emphasis">
            Our AI analyzes job descriptions to create perfectly tailored resumes
          </p>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="pa-4 h-100 value-card" elevation="2">
            <v-icon size="48" color="primary" class="mb-4">mdi-magnify</v-icon>
            <h3 class="text-h5 font-weight-bold mb-3">Keyword Optimization</h3>
            <p class="text-body-1">
              Automatically identifies and incorporates key terms from job descriptions.
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="pa-4 h-100 value-card" elevation="2">
            <v-icon size="48" color="primary" class="mb-4">mdi-robot</v-icon>
            <h3 class="text-h5 font-weight-bold mb-3">ATS Compliance</h3>
            <p class="text-body-1">
              Ensures your resume passes automated screening systems with proper formatting.
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="pa-4 h-100 value-card" elevation="2">
            <v-icon size="48" color="primary" class="mb-4">mdi-account-tie</v-icon>
            <h3 class="text-h5 font-weight-bold mb-3">Skills Matching</h3>
            <p class="text-body-1">
              Highlights your most relevant skills and experience for each position.
            </p>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Social Proof Section -->
    <v-container class="py-16 social-proof-section">
      <v-row>
        <v-col cols="12" class="text-center mb-12">
          <h2 class="text-h3 font-weight-bold mb-3">Trusted by Professionals</h2>
          <p class="text-h6 text-medium-emphasis">
            Join thousands who have landed their dream jobs
          </p>
        </v-col>
        
        <v-col cols="12" md="4" class="text-center">
          <div class="text-h4 font-weight-bold mb-2">4.9/5</div>
          <v-rating
            v-model="rating"
            color="amber"
            dense
            half-increments
            readonly
            size="24"
            class="mb-2"
          ></v-rating>
          <p class="text-body-1">Average User Rating</p>
        </v-col>
        
        <v-col cols="12" md="4" class="text-center">
          <div class="text-h4 font-weight-bold mb-2">10,000+</div>
          <p class="text-body-1">Resumes Created</p>
        </v-col>
        
        <v-col cols="12" md="4" class="text-center">
          <div class="text-h4 font-weight-bold mb-2">85%</div>
          <p class="text-body-1">Interview Rate</p>
        </v-col>
      </v-row>
    </v-container>

    <!-- Call to Action Section -->
    <v-row class="bg-secondary py-16 cta-section">
      <v-container>
        <v-row justify="center" align="center">
          <v-col cols="12" md="8" class="text-center">
            <h2 class="text-h3 font-weight-bold mb-4 text-white">
              Ready to Build Your Professional Resume?
            </h2>
            <p class="text-h6 mb-6 text-white">
              Join thousands of job seekers who have successfully landed their dream jobs
            </p>
            <v-btn
              :to="{ path: '/login' }"
              size="x-large"
              color="orange-lighten-2"
              class="text-grey-darken-4 rounded-pill px-8"
              elevation="4"
            >
              Start Building Now
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const rating = ref(4.9)
</script>

<style scoped>
.hero-section {
  background: linear-gradient(45deg, rgb(25, 118, 210), rgb(21, 101, 192));
}

.timer-comparison {
  display: flex;
  align-items: center;
}

.v-chip {
  font-weight: 600;
  font-size: 1.1rem;
  padding: 8px 16px;
}

.v-card {
  transition: transform 0.3s ease;
}

.v-card:hover {
  transform: translateY(-5px);
}

/* Mobile responsive styles */
@media (max-width: 960px) {
  .hero-section {
    min-height: 60vh !important;
  }
  
  .hero-section .v-row {
    min-height: 60vh !important;
  }
  
  .hero-section h1 {
    font-size: 2rem !important;
    line-height: 1.2 !important;
    margin-bottom: 1rem !important;
  }
  
  .hero-section p {
    font-size: 1.1rem !important;
    margin-bottom: 1.5rem !important;
  }
  
  .hero-section .v-btn {
    font-size: 1rem !important;
    padding: 12px 24px !important;
  }
  
  .features-section h2 {
    font-size: 1.8rem !important;
  }
  
  .features-section p {
    font-size: 1rem !important;
  }
  
  .feature-card h3 {
    font-size: 1.3rem !important;
  }
  
  .feature-card p {
    font-size: 0.9rem !important;
  }
  
  .cta-section h2 {
    font-size: 1.8rem !important;
  }
  
  .cta-section p {
    font-size: 1rem !important;
  }
}

@media (max-width: 600px) {
  .hero-section {
    min-height: 50vh !important;
  }
  
  .hero-section .v-container {
    padding-left: 16px !important;
    padding-right: 16px !important;
  }
  
  .hero-section .v-col {
    padding-left: 16px !important;
    padding-right: 16px !important;
  }
  
  .hero-section .v-col:first-child {
    text-align: center !important;
    display: block !important;
  }
  
  .hero-section .v-col:first-child .v-btn {
    margin: 0 auto !important;
  }
  
  .hero-section .v-row {
    min-height: 50vh !important;
  }
  
  .hero-section h1 {
    font-size: 1.6rem !important;
    line-height: 1.1 !important;
    margin-bottom: 0.8rem !important;
  }
  
  .hero-section p {
    font-size: 1rem !important;
    margin-bottom: 1.2rem !important;
  }
  
  .hero-section .v-btn {
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
  }
  
  .features-section h2 {
    font-size: 1.5rem !important;
  }
  
  .features-section p {
    font-size: 0.9rem !important;
  }
  
  .feature-card h3 {
    font-size: 1.2rem !important;
  }
  
  .feature-card p {
    font-size: 0.85rem !important;
  }
  
  .cta-section h2 {
    font-size: 1.5rem !important;
  }
  
  .cta-section p {
    font-size: 0.9rem !important;
  }
  
  .v-container {
    padding: 16px !important;
  }
  
  .py-16 {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
  }
}
</style>
