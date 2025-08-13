<template>
  <v-container fluid class="pa-0">
    <!-- Hero Section -->
    <section class="hero-section">
      <v-container class="fill-height">
        <v-row align="center">
          <v-col cols="12" md="6" class="text-center text-md-left">
            <h1 class="text-h2 font-weight-bold mb-4">Land Your Dream Job with a Perfect Resume</h1>
            <p class="text-h6 mb-8">
              Create a professional, ATS-friendly resume in minutes. Our AI-powered platform helps you stand out from the competition and get hired faster.
            </p>
            <v-btn :to="{ path: '/login' }" size="x-large" color="orange-lighten-2" class="text-white rounded-lg px-10" elevation="6">
              Get Started for Free
            </v-btn>
          </v-col>
          <v-col cols="12" md="6" class="d-none d-md-flex justify-center">
            <v-img src="/resume-preview.png" max-width="450" class="elevation-12 rounded-lg"></v-img>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Features Section -->
    <section class="py-16 features-section">
      <v-container>
        <v-row>
          <v-col cols="12" class="text-center mb-12">
            <h2 class="text-h3 font-weight-bold">Why Choose Resume Genie?</h2>
            <p class="text-h6 text-medium-emphasis mt-4">Everything you need to create a job-winning resume.</p>
          </v-col>
          <v-col v-for="feature in features" :key="feature.title" cols="12" md="4">
            <v-card class="pa-6 h-100 text-center feature-card" elevation="4" rounded="lg">
              <v-icon size="56" color="primary" class="mb-6">{{ feature.icon }}</v-icon>
              <h3 class="text-h5 font-weight-bold mb-4">{{ feature.title }}</h3>
              <p class="text-body-1">{{ feature.description }}</p>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- How It Works Section -->
    <section class="py-16 bg-grey-lighten-5">
      <v-container>
        <v-row>
          <v-col cols="12" class="text-center mb-12">
            <h2 class="text-h3 font-weight-bold">How It Works</h2>
            <p class="text-h6 text-medium-emphasis mt-4">Create your perfect resume in 3 simple steps.</p>
          </v-col>
          <v-col v-for="(step, i) in steps" :key="i" cols="12" md="4">
            <div class="text-center">
              <v-avatar color="primary" size="80" class="mb-6 elevation-4">
                <v-icon size="40" color="white">{{ step.icon }}</v-icon>
              </v-avatar>
              <h3 class="text-h5 font-weight-bold mb-4">{{ step.title }}</h3>
              <p class="text-body-1">{{ step.description }}</p>
            </div>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Testimonials Section -->
    <section class="py-16 testimonials-section">
      <v-container>
        <v-row>
          <v-col cols="12" class="text-center mb-12">
            <h2 class="text-h3 font-weight-bold">What Our Users Say</h2>
          </v-col>
          <v-col v-for="(testimonial, i) in testimonials" :key="i" cols="12" md="4">
            <v-card class="pa-6 h-100" elevation="4" rounded="lg">
              <v-rating v-model="testimonial.rating" color="amber" dense half-increments readonly class="mb-4"></v-rating>
              <p class="text-body-1 mb-6">"{{ testimonial.text }}"</p>
              <div class="d-flex align-center">
                <v-avatar color="primary" size="48" class="mr-4">
                  <span class="text-h6">{{ testimonial.author.charAt(0) }}</span>
                </v-avatar>
                <div>
                  <div class="font-weight-bold">{{ testimonial.author }}</div>
                  <div class="text-caption">{{ testimonial.position }}</div>
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </section>

    <!-- Call to Action Section -->
    <section class="py-16 cta-section">
      <v-container>
        <v-row justify="center">
          <v-col cols="12" md="8" class="text-center">
            <h2 class="text-h3 font-weight-bold mb-6">Ready to Get Started?</h2>
            <p class="text-h6 mb-8">
              Take the next step in your career. Create a resume that gets you noticed.
            </p>
            <v-btn :to="{ path: '/login' }" size="x-large" color="orange-lighten-2" class="text-white rounded-lg px-12" elevation="6">
              Build My Resume Now
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </section>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const features = ref([
  {
    icon: 'mdi-auto-fix',
    title: 'AI-Powered Content',
    description: 'Our AI analyzes your profile and job descriptions to write compelling, keyword-optimized resume content.'
  },
  {
    icon: 'mdi-file-document-multiple-outline',
    title: 'Professional Templates',
    description: 'Choose from a variety of professionally designed templates that are proven to impress recruiters.'
  },
  {
    icon: 'mdi-target-account',
    title: 'ATS-Friendly',
    description: 'Our resumes are designed to pass through Applicant Tracking Systems (ATS) and get seen by human eyes.'
  }
])

const steps = ref([
  {
    icon: 'mdi-account-plus-outline',
    title: 'Create Your Profile',
    description: 'Sign up and fill out your profile with your experience, skills, and education.'
  },
  {
    icon: 'mdi-file-edit-outline',
    title: 'Customize Your Resume',
    description: 'Our AI will generate a resume for you. Fine-tune the content and choose a template that fits your style.'
  },
  {
    icon: 'mdi-download-outline',
    title: 'Download and Apply',
    description: 'Download your new resume as a PDF or Word document and start applying for your dream job.'
  }
])

const testimonials = ref([
  {
    rating: 5,
    text: 'Resume Genie helped me land my dream job in just two weeks. The AI-powered suggestions were a game-changer!',
    author: 'John Doe',
    position: 'Software Engineer'
  },
  {
    rating: 4.5,
    text: 'I was struggling to get interviews until I used Resume Genie. The professional templates made all the difference.',
    author: 'Jane Smith',
    position: 'Product Manager'
  },
  {
    rating: 5,
    text: 'As a recent graduate, I had no idea how to write a resume. Resume Genie made it easy and stress-free.',
    author: 'Peter Jones',
    position: 'Marketing Associate'
  }
])
</script>

<style scoped>
.hero-section {
  background: linear-gradient(to top right, #E3F2FD, #BBDEFB);
  min-height: 90vh;
  display: flex;
  align-items: center;
}

.feature-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.1);
}

.cta-section {
  background: linear-gradient(45deg, #1976D2, #2196F3);
  color: white;
}

@media (max-width: 960px) {
  .hero-section {
    min-height: 70vh;
    text-align: center;
  }
  .text-h2 {
    font-size: 2.5rem !important;
  }
}
</style>
