<template>
  <v-container fluid class="pa-0">
    <!-- Hero Section -->
    <v-row class="bg-primary hero-section" style="min-height: 80vh">
      <v-container>
        <v-row align="center" style="min-height: 80vh">
          <v-col cols="12" md="6">
            <h1 class="text-h2 font-weight-bold mb-4 text-white">
              Create Professional Resumes in Minutes
            </h1>
            <p class="text-h6 mb-6 text-white">
              Build stunning, ATS-friendly resumes that help you stand out and land your dream job.
            </p>
            <v-btn
              :to="{ path: '/login' }"
              size="x-large"
              color="white"
              class="text-primary rounded-pill"
            >
              Get Started
            </v-btn>
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

    <!-- Features Section -->
    <v-container class="py-16 features-section">
      <v-row>
        <v-col cols="12" class="text-center mb-12">
          <h2 class="text-h3 font-weight-bold mb-3">Why Choose Us?</h2>
          <p class="text-h6 text-medium-emphasis">
            Everything you need to create a professional resume
          </p>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="pa-4 h-100 feature-card" elevation="2">
            <v-icon size="48" color="primary" class="mb-4">mdi-file-document-check</v-icon>
            <h3 class="text-h5 font-weight-bold mb-3">ATS-Friendly Templates</h3>
            <p class="text-body-1">
              Our templates are designed to pass Applicant Tracking Systems and reach human recruiters.
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="pa-4 h-100 feature-card" elevation="2">
            <v-icon size="48" color="primary" class="mb-4">mdi-lightning-bolt</v-icon>
            <h3 class="text-h5 font-weight-bold mb-3">Easy to Use</h3>
            <p class="text-body-1">
              Intuitive interface that guides you through the resume creation process step by step.
            </p>
          </v-card>
        </v-col>

        <v-col cols="12" md="4">
          <v-card class="pa-4 h-100 feature-card" elevation="2">
            <v-icon size="48" color="primary" class="mb-4">mdi-palette</v-icon>
            <h3 class="text-h5 font-weight-bold mb-3">Customizable Design</h3>
            <p class="text-body-1">
              Personalize fonts, colors, and layouts while maintaining professional standards.
            </p>
          </v-card>
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
              color="white"
              class="text-secondary rounded-pill"
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
// No additional script needed for the landing page
</script>

<style scoped>
.hero-section {
  background: linear-gradient(45deg, rgb(25, 118, 210), rgb(21, 101, 192));
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
    padding: 8px !important;
  }
  
  .py-16 {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
  }
}
</style>
