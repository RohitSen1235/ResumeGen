<template>
  <v-container class="about-us-view" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row justify="center">
      <v-col cols="12" lg="10" xl="8">
        <v-card 
          class="pa-md-8 pa-4" 
          elevation="12" 
          rounded="xl" 
          style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.9);"
        >
          <v-card-title class="text-h4 font-weight-bold mb-6 text-grey-darken-3 text-center">
            <v-icon icon="mdi-account-group" class="mr-3" color="primary"></v-icon>
            About ResumeGenie
          </v-card-title>
          
          <v-card-text class="pa-0">
            <div class="about-content">
              <!-- Hero Section -->
              <div class="hero-section mb-8">
                <div class="text-center mb-6">
                  <v-icon icon="mdi-rocket-launch" size="80" color="primary" class="mb-4"></v-icon>
                  <h2 class="text-h5 font-weight-bold text-primary mb-3">Empowering Your Career Journey</h2>
                  <p class="text-h6 text-grey-darken-1">AI-powered resume optimization for the modern job seeker</p>
                </div>
              </div>

              <!-- Mission Section -->
              <v-row class="mb-8">
                <v-col cols="12" md="6">
                  <v-card variant="tonal" color="primary" class="pa-6 h-100">
                    <div class="text-center">
                      <v-icon icon="mdi-target" size="48" color="primary" class="mb-3"></v-icon>
                      <h3 class="text-h6 font-weight-bold mb-3">Our Mission</h3>
                      <p class="text-body-1">
                        To democratize career success by providing intelligent, personalized resume optimization 
                        that helps job seekers present their best professional selves to potential employers.
                      </p>
                    </div>
                  </v-card>
                </v-col>
                <v-col cols="12" md="6">
                  <v-card variant="tonal" color="secondary" class="pa-6 h-100">
                    <div class="text-center">
                      <v-icon icon="mdi-eye" size="48" color="secondary" class="mb-3"></v-icon>
                      <h3 class="text-h6 font-weight-bold mb-3">Our Vision</h3>
                      <p class="text-body-1">
                        A world where every qualified candidate has an equal opportunity to showcase their 
                        skills and experience through professionally optimized resumes that stand out in today's competitive job market.
                      </p>
                    </div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Story Section -->
              <div class="story-section mb-8">
                <h3 class="text-h5 font-weight-bold text-primary mb-4 text-center">Our Story</h3>
                <v-card variant="outlined" class="pa-6">
                  <div class="markdown-content" v-html="storyContent"></div>
                </v-card>
              </div>

              <!-- Features Section -->
              <div class="features-section mb-8">
                <h3 class="text-h5 font-weight-bold text-primary mb-6 text-center">What Makes Us Different</h3>
                <v-row>
                  <v-col cols="12" md="4" v-for="feature in features" :key="feature.title">
                    <v-card variant="outlined" class="pa-4 h-100 text-center">
                      <v-icon :icon="feature.icon" size="48" :color="feature.color" class="mb-3"></v-icon>
                      <h4 class="text-h6 font-weight-bold mb-2">{{ feature.title }}</h4>
                      <p class="text-body-2">{{ feature.description }}</p>
                    </v-card>
                  </v-col>
                </v-row>
              </div>

              <!-- Values Section -->
              <div class="values-section mb-8">
                <h3 class="text-h5 font-weight-bold text-primary mb-6 text-center">Our Core Values</h3>
                <v-row>
                  <v-col cols="12" md="6" lg="3" v-for="value in values" :key="value.title">
                    <div class="text-center">
                      <v-avatar size="80" :color="value.color" class="mb-3">
                        <v-icon :icon="value.icon" size="40" color="white"></v-icon>
                      </v-avatar>
                      <h4 class="text-h6 font-weight-bold mb-2">{{ value.title }}</h4>
                      <p class="text-body-2">{{ value.description }}</p>
                    </div>
                  </v-col>
                </v-row>
              </div>

              <!-- Commitment Section -->
              <div class="commitment-section mb-8">
                <v-card color="primary" variant="flat" class="pa-6">
                  <div class="text-center text-white">
                    <v-icon icon="mdi-shield-check" size="60" color="white" class="mb-4"></v-icon>
                    <h3 class="text-h5 font-weight-bold mb-4">Our Commitment to You</h3>
                    <div class="markdown-content-white" v-html="commitmentContent"></div>
                  </div>
                </v-card>
              </div>

              <!-- Contact Section -->
              <div class="contact-section">
                <h3 class="text-h5 font-weight-bold text-primary mb-6 text-center">Get in Touch</h3>
                <v-row justify="center">
                  <v-col cols="12" md="8">
                    <v-card variant="outlined" class="pa-6">
                      <div class="text-center">
                        <p class="text-body-1 mb-4">
                          Have questions, feedback, or need support? We'd love to hear from you!
                        </p>
                        <div class="contact-info">
                          <div class="mb-3">
                            <v-icon icon="mdi-email" class="mr-2" color="primary"></v-icon>
                            <strong>Email:</strong> support@ResumeGenie.com
                          </div>
                          <div class="mb-3">
                            <v-icon icon="mdi-clock" class="mr-2" color="primary"></v-icon>
                            <strong>Response Time:</strong> Within 24 hours
                          </div>
                          <div>
                            <v-icon icon="mdi-web" class="mr-2" color="primary"></v-icon>
                            <strong>Website:</strong> www.ResumeGenie.com
                          </div>
                        </div>
                      </div>
                    </v-card>
                  </v-col>
                </v-row>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'

const storyContent = marked(`ResumeGenie was born from a simple observation: **talented professionals were struggling to get noticed** in an increasingly competitive job market.

Our founders, experienced in both **technology and human resources**, witnessed countless qualified candidates being overlooked simply because their resumes didn't effectively communicate their value proposition.

**The problem was clear:**
- Traditional resume writing is time-consuming and expensive
- Generic templates don't capture individual strengths
- Job seekers lack insight into what employers actually want
- ATS systems filter out qualified candidates due to formatting issues

**Our solution leverages cutting-edge AI** to analyze job descriptions and optimize resumes accordingly, while maintaining the human touch that makes each application authentic and personal.

Since our launch, we've helped **thousands of professionals** land interviews at their dream companies, from startups to Fortune 500 organizations.`) as string

const commitmentContent = marked(`**We believe in transparency, accuracy, and your success.**

- **No false promises** - We're honest about what AI can and cannot do
- **Your data is secure** - We never sell or share your personal information  
- **Continuous improvement** - We constantly update our AI based on industry trends
- **Human oversight** - Every feature is designed with human review in mind
- **Affordable access** - Professional resume optimization shouldn't break the bank`) as string

const features = ref([
  {
    title: "AI-Powered Analysis",
    description: "Advanced algorithms analyze job descriptions and optimize your resume content for maximum impact and ATS compatibility.",
    icon: "mdi-brain",
    color: "primary"
  },
  {
    title: "Human-Centric Design",
    description: "While AI provides suggestions, you maintain full control. Every recommendation requires your review and approval.",
    icon: "mdi-account-heart",
    color: "secondary"
  },
  {
    title: "Industry Expertise",
    description: "Our AI is trained on successful resumes across multiple industries and job levels, from entry-level to executive positions.",
    icon: "mdi-briefcase-variant",
    color: "success"
  },
  {
    title: "Privacy First",
    description: "Your personal information and resume content are encrypted and secure. We never share your data with third parties.",
    icon: "mdi-shield-lock",
    color: "warning"
  },
  {
    title: "Multiple Formats",
    description: "Download your optimized resume in PDF or Word format, with professional templates designed for modern hiring practices.",
    icon: "mdi-file-multiple",
    color: "info"
  },
  {
    title: "Continuous Updates",
    description: "Our platform evolves with hiring trends, ensuring your resume stays current with industry best practices.",
    icon: "mdi-update",
    color: "error"
  }
])

const values = ref([
  {
    title: "Integrity",
    description: "We're transparent about our AI's capabilities and limitations, ensuring you make informed decisions.",
    icon: "mdi-handshake",
    color: "primary"
  },
  {
    title: "Innovation",
    description: "We continuously improve our technology to provide cutting-edge resume optimization solutions.",
    icon: "mdi-lightbulb",
    color: "secondary"
  },
  {
    title: "Empowerment",
    description: "We give job seekers the tools and insights they need to take control of their career journey.",
    icon: "mdi-rocket",
    color: "success"
  },
  {
    title: "Accessibility",
    description: "Professional resume optimization should be available to everyone, regardless of budget or background.",
    icon: "mdi-account-group",
    color: "warning"
  }
])
</script>

<style scoped>
.about-us-view {
  min-height: 100vh;
  padding: 24px 0;
}

.about-content {
  max-height: 85vh;
  overflow-y: auto;
}

.hero-section {
  text-align: center;
  padding: 20px 0;
}

.markdown-content {
  line-height: 1.7;
  font-size: 0.95rem;
}

.markdown-content-white {
  line-height: 1.7;
  font-size: 0.95rem;
  color: white;
}

/* Markdown styling */
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4) {
  color: #1976d2;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.markdown-content-white :deep(h1),
.markdown-content-white :deep(h2),
.markdown-content-white :deep(h3),
.markdown-content-white :deep(h4) {
  color: white;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.markdown-content :deep(p) {
  margin: 12px 0;
  color: #424242;
}

.markdown-content-white :deep(p) {
  margin: 12px 0;
  color: white;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 12px 0;
  padding-left: 20px;
}

.markdown-content-white :deep(ul),
.markdown-content-white :deep(ol) {
  margin: 12px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 6px 0;
  color: #424242;
}

.markdown-content-white :deep(li) {
  margin: 6px 0;
  color: white;
}

.markdown-content :deep(strong) {
  color: #1976d2;
  font-weight: 600;
}

.markdown-content-white :deep(strong) {
  color: white;
  font-weight: 600;
}

.contact-info {
  text-align: left;
  display: inline-block;
}

/* Custom scrollbar */
.about-content::-webkit-scrollbar {
  width: 8px;
}

.about-content::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 4px;
}

.about-content::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-primary), 0.5);
  border-radius: 4px;
}

.about-content::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-primary), 0.7);
}

/* Mobile responsiveness */
@media (max-width: 960px) {
  .about-content {
    max-height: 80vh;
  }
  
  .markdown-content,
  .markdown-content-white {
    font-size: 0.9rem;
  }
  
  .hero-section {
    padding: 10px 0;
  }
}

@media (max-width: 600px) {
  .about-us-view {
    padding: 12px 0;
  }
  
  .about-content {
    max-height: 75vh;
  }
  
  .markdown-content,
  .markdown-content-white {
    font-size: 0.85rem;
  }
  
  .contact-info {
    text-align: center;
  }
}
</style>
