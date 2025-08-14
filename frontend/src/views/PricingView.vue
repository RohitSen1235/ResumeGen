<template>
  <v-container class="py-16">
    <v-row justify="center">
      <v-col cols="12" class="text-center mb-12">
        <h1 class="text-h3 font-weight-bold mb-4" style="color: #1565C0;">Find the Perfect Plan</h1>
        <p class="text-h6 font-weight-light text-grey-darken-1">
          Unlock your career potential with our tailored credit plans.
        </p>
      </v-col>
    </v-row>

    <v-row justify="center" align="center">
      <v-col
        v-for="(plan, i) in plans"
        :key="plan.name"
        cols="12"
        md="4"
        class="d-flex"
      >
        <v-card 
          :class="['mx-auto', 'd-flex', 'flex-column', 'plan-card', { 'popular-plan': plan.popular }]"
          max-width="380"
          :elevation="plan.popular ? 16 : 4"
          rounded="lg"
        >
          <v-card-title class="justify-center text-h5 font-weight-bold pt-6 pb-2">
            <v-chip
              v-if="plan.popular"
              color="orange-lighten-2"
              variant="elevated"
              class="popular-badge"
            >
              Most Popular
            </v-chip>
            {{ plan.name }}
          </v-card-title>
          <v-card-subtitle class="text-center text-body-1">{{ plan.credits }} Credits</v-card-subtitle>
          
          <v-card-text class="text-center flex-grow-1">
            <div class="d-flex justify-center align-center my-6">
              <span class="text-h5 font-weight-bold">₹</span>
              <span class="text-h2 font-weight-black">{{ plan.price }}</span>
            </div>
            
            <v-list-item v-for="feature in plan.features" :key="feature" class="px-0 text-left">
              <template v-slot:prepend>
                <v-icon color="green" class="mr-3">mdi-check-circle</v-icon>
              </template>
              <v-list-item-title class="text-body-1">{{ feature }}</v-list-item-title>
            </v-list-item>
          </v-card-text>
          
          <v-card-actions class="justify-center pa-6">
            <v-btn 
              :color="plan.popular ? 'orange-lighten-2' : '#1565C0'"
              :variant="plan.popular ? 'elevated' : 'outlined'"
              size="x-large"
              block
            >
              Choose Plan
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-row justify="center" class="mt-16">
      <v-col cols="12" md="8">
        <h2 class="text-h4 font-weight-bold text-center mb-8">Frequently Asked Questions</h2>
        <v-expansion-panels variant="accordion">
          <v-expansion-panel
            v-for="faq in faqs"
            :key="faq.question"
            :title="faq.question"
            :text="faq.answer"
          ></v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
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
            '10 AI-powered resume reviews',
            'Access to all templates',
            'PDF downloads',
          ],
        },
        {
          name: 'Pro',
          credits: 30,
          price: 1999,
          popular: true,
          features: [
            '30 AI-powered resume reviews',
            'Access to all templates',
            'PDF downloads',
            'Cover letter generator',
          ],
        },
        {
          name: 'Ultimate',
          credits: 100,
          price: 3999,
          popular: false,
          features: [
            '100 AI-powered resume reviews',
            'Access to all templates',
            'PDF downloads',
            'Cover letter generator',
            'LinkedIn profile optimization',
          ],
        },
      ],
      faqs: [
        {
          question: 'What are credits and how do I use them?',
          answer: 'Credits are used to access our premium features, such as AI-powered resume reviews and cover letter generation. Each time you use a premium feature, one credit is deducted from your account.',
        },
        {
          question: 'Do my credits expire?',
          answer: 'No, your credits never expire. You can use them whenever you need them.',
        },
        {
          question: 'Can I upgrade my plan later?',
          answer: 'Yes, you can upgrade your plan at any time. Simply choose a new plan and your remaining credits will be carried over.',
        },
        {
          question: 'What payment methods do you accept?',
          answer: 'We accept all major credit cards, as well as PayPal.',
        },
      ],
    };
  },
});
</script>

<style scoped>
.plan-card {
  transition: all 0.3s ease-in-out;
  border: 1px solid #E0E0E0;
  position: relative;
  overflow: visible;
}
.plan-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.12) !important;
}

.popular-plan {
  border: 2px solid #FB8C00;
  transform: scale(1.05);
}

.popular-plan:hover {
  transform: scale(1.05) translateY(-8px);
}

.popular-badge {
  position: absolute;
  top: -16px;
  left: 50%;
  transform: translateX(-50%);
  font-weight: bold;
}

.v-list-item {
  min-height: auto;
  padding-top: 8px;
  padding-bottom: 8px;
}

.v-expansion-panel-title {
  font-weight: bold;
}
</style>
