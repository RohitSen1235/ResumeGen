<template>
  <div class="pricing-page-bg">
    <v-container class="py-12">
      <v-row justify="center">
        <v-col cols="12" class="text-center mb-10">
          <h1 class="text-h3 font-weight-bold mb-4 text-grey-darken-3">Pricing Plans</h1>
          <p class="text-h6 font-weight-light text-grey-darken-1">
            Choose the plan that's right for your career goals.
          </p>
        </v-col>
      </v-row>

      <v-row justify="center" align="stretch">
        <v-col
          v-for="(plan, i) in plans"
          :key="plan.name"
          cols="12"
          md="4"
        >
          <v-card 
            :class="['d-flex', 'flex-column', 'h-100', 'plan-card', { 'popular-plan': plan.popular }]"
            :elevation="plan.popular ? 16 : 8"
            rounded="xl"
          >
            <v-card-title class="justify-center text-h4 font-weight-bold pt-12 pb-4">
              {{ plan.name }}
            </v-card-title>
            <div v-if="plan.popular" class="popular-badge-container">
              <v-chip
                color="orange-lighten-2"
                variant="elevated"
                class="popular-badge"
                prepend-icon="mdi-star"
              >
                Most Popular
              </v-chip>
            </div>
            <v-card-subtitle class="text-center text-h6">{{ plan.credits }} Credits</v-card-subtitle>
            
            <v-card-text class="text-center flex-grow-1 pa-8">
              <div class="d-flex justify-center align-baseline my-8">
                <span class="text-h4 font-weight-bold text-grey-darken-2">₹</span>
                <span class="text-h2 font-weight-black text-grey-darken-4">{{ plan.price }}</span>
              </div>
              
              <v-divider class="mb-6"></v-divider>

              <v-list-item v-for="feature in plan.features" :key="feature" class="px-0 text-left py-2">
                <template v-slot:prepend>
                  <v-icon color="primary" class="mr-4">mdi-check-circle-outline</v-icon>
                </template>
                <v-list-item-title class="text-body-1">{{ feature }}</v-list-item-title>
              </v-list-item>
            </v-card-text>
            
            <v-card-actions class="justify-center pa-8">
              <v-btn 
                :color="plan.popular ? 'orange-lighten-2' : 'primary'"
                :variant="plan.popular ? 'elevated' : 'flat'"
                size="x-large"
                block
                class="font-weight-bold"
                rounded="lg"
              >
                Get Started
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>

      <v-row justify="center" class="mt-16">
        <v-col cols="12" md="9">
          <v-card
            elevation="8"
            rounded="xl"
            class="faq-card"
          >
            <v-card-title class="text-h4 font-weight-bold text-center pt-8 pb-6 text-grey-darken-3">
              Frequently Asked Questions
            </v-card-title>
            <v-card-text>
              <v-expansion-panels variant="accordion" class="faq-panels">
                <v-expansion-panel
                  v-for="faq in faqs"
                  :key="faq.question"
                  class="faq-panel"
                  elevation="0"
                >
                  <v-expansion-panel-title class="text-h6 font-weight-medium">{{ faq.question }}</v-expansion-panel-title>
                  <v-expansion-panel-text class="text-body-1 pa-5">
                    {{ faq.answer }}
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'PricingView',
  data() {
    return {
      plans: [
        {
          name: 'Starter',
          credits: 10,
          price: 899,
          popular: false,
          features: [
            '10 AI Resume Reviews',
            'Access to All Templates',
            'Unlimited PDF Downloads',
          ],
        },
        {
          name: 'Pro',
          credits: 30,
          price: 1999,
          popular: true,
          features: [
            '30 AI Resume Reviews',
            'Access to All Templates',
            'Unlimited PDF Downloads',
            'AI Cover Letter Generator',
          ],
        },
        {
          name: 'Ultimate',
          credits: 100,
          price: 3999,
          popular: false,
          features: [
            '100 AI Resume Reviews',
            'Access to All Templates',
            'Unlimited PDF Downloads',
            'AI Cover Letter Generator',
            'LinkedIn Profile Optimization',
          ],
        },
      ],
      faqs: [
        {
          question: 'What are credits and how do I use them?',
          answer: 'Credits are your key to unlocking our premium AI features. One credit is used for one major action, like a comprehensive resume review or generating a tailored cover letter. This allows you to use our most powerful tools exactly when you need them.',
        },
        {
          question: 'Do my credits ever expire?',
          answer: 'No, your credits are yours to keep. They never expire, so you can use them at your own pace, whenever you need a career boost.',
        },
        {
          question: 'Can I upgrade my plan later?',
          answer: 'Absolutely! You can upgrade your plan at any time from your account dashboard. Any unused credits will automatically carry over to your new plan.',
        },
        {
          question: 'What payment methods do you accept?',
          answer: 'We accept all major credit cards (Visa, Mastercard, American Express) and PayPal for your convenience.',
        },
      ],
    };
  },
});
</script>

<style scoped>
.pricing-page-bg {
  background: linear-gradient(to top right, #E3F2FD, #BBDEFB);
  min-height: 100vh;
}

.plan-card, .faq-card {
  backdrop-filter: blur(10px);
  background-color: rgba(255, 255, 255, 0.8) !important;
  transition: all 0.3s ease-in-out;
}

.plan-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.15) !important;
}

.popular-plan {
  border: 2px solid #FFB74D; /* orange-lighten-2 */
  transform: scale(1.03);
  position: relative;
  z-index: 1;
}

.popular-badge-container {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.popular-badge {
  font-weight: bold;
  font-size: 0.9rem;
  padding: 8px 20px;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.v-list-item {
  min-height: auto;
}

.faq-panels {
  background-color: transparent;
}

.faq-panel {
  background-color: transparent !important;
  border-bottom: 1px solid #e0e0e0;
}

.faq-panel:last-child {
  border-bottom: none;
}

.v-expansion-panel-title {
  color: #424242; /* grey-darken-3 */
}

.v-expansion-panel-text {
  color: #616161; /* grey-darken-2 */
}
</style>
