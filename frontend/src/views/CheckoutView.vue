<template>
  <v-container class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <div v-if="selectedPlan">
          <h1 class="text-h3 font-weight-bold text-center mb-4">Complete Your Purchase</h1>
          <p class="text-h6 text-center text-grey-darken-1 mb-10">
            You're just one step away from unlocking premium features.
          </p>

          <v-row>
            <!-- Order Summary -->
            <v-col cols="12" md="6">
              <v-card elevation="4" rounded="xl" class="fill-height">
                <v-card-title class="text-h5 font-weight-bold d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-cart-outline</v-icon>
                  Order Summary
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text>
                  <v-list-item class="pa-0">
                    <v-list-item-title class="text-subtitle-1">{{ selectedPlan.name }} Plan</v-list-item-title>
                    <template v-slot:append>
                      <span class="text-h6 font-weight-bold">₹{{ selectedPlan.price }}</span>
                    </template>
                  </v-list-item>
                  <v-divider class="my-4"></v-divider>
                  <div class="d-flex justify-space-between text-h6 font-weight-bold">
                    <span>Total Amount</span>
                    <span class="text-primary">₹{{ selectedPlan.price }}</span>
                  </div>
                </v-card-text>

                <v-card-text>
                  <h3 class="text-h6 font-weight-medium mb-3">What's Included:</h3>
                  <v-list density="compact">
                    <v-list-item v-for="(feature, i) in selectedPlan.features" :key="i" class="px-0">
                      <template v-slot:prepend>
                        <v-icon color="success" class="mr-3">mdi-check-circle</v-icon>
                      </template>
                      <v-list-item-title>{{ feature }}</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>

            <!-- Customer Details & Payment -->
            <v-col cols="12" md="6">
              <v-card elevation="4" rounded="xl" class="fill-height d-flex flex-column">
                <v-card-title class="text-h5 font-weight-bold d-flex align-center">
                  <v-icon class="mr-2" color="primary">mdi-account-circle-outline</v-icon>
                  Your Details
                </v-card-title>
                <v-divider></v-divider>
                <v-card-text>
                  <v-list>
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Email Address</v-list-item-title>
                      <v-list-item-subtitle>{{ authStore.user?.email }}</v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                  <v-alert v-if="error" type="error" class="mt-4">{{ error }}</v-alert>
                </v-card-text>
                <v-spacer></v-spacer>
                <v-card-actions class="pa-4">
                  <v-btn
                    color="orange-lighten-2"
                    size="x-large"
                    block
                    @click="handlePayment"
                    :loading="loading"
                    prepend-icon="mdi-lock-outline"
                  >
                    Proceed to Secure Payment
                  </v-btn>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </div>
        <v-alert v-else type="warning" class="mt-4" icon="mdi-alert-circle-outline">
          No plan selected. Please <router-link to="/pricing">go back</router-link> and choose a plan.
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue';
import { usePaymentStore } from '@/store/payment';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';

declare const Cashfree: any;

export default defineComponent({
  name: 'CheckoutView',
  setup() {
    const paymentStore = usePaymentStore();
    const authStore = useAuthStore();
    const router = useRouter();

    const selectedPlan = computed(() => paymentStore.selectedPlan);
    const loading = computed(() => paymentStore.loading);
    const error = computed(() => paymentStore.error);

    const handlePayment = async () => {
      if (selectedPlan.value) {
        try {
          const order = await paymentStore.createCashfreeOrder(selectedPlan.value.price);
          if (order.payment_session_id) {
            const cashfree = await Cashfree({
              mode: "sandbox"
            });
            cashfree.checkout({
              paymentSessionId: order.payment_session_id,
              returnUrl: `${window.location.origin}/payment/callback`
            });
          }
        } catch (err) {
          console.error('Payment initiation failed:', err);
        }
      }
    };

    onMounted(() => {
      if (!selectedPlan.value) {
        router.push({ name: 'Pricing' });
      }
      authStore.fetchUser();
    });

    return {
      selectedPlan,
      loading,
      error,
      authStore,
      handlePayment,
    };
  },
});
</script>
