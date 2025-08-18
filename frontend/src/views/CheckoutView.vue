<template>
  <v-container class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="6">
        <v-card v-if="selectedPlan" elevation="8" rounded="xl">
          <v-card-title class="text-h4 font-weight-bold text-center pt-8 pb-6">
            Checkout Summary
          </v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item>
                <v-list-item-title class="font-weight-bold">Plan</v-list-item-title>
                <v-list-item-subtitle>{{ selectedPlan.name }}</v-list-item-subtitle>
              </v-list-item>
              <v-list-item>
                <v-list-item-title class="font-weight-bold">Price</v-list-item-title>
                <v-list-item-subtitle>₹{{ selectedPlan.price }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
            <v-alert v-if="error" type="error" class="mt-4">{{ error }}</v-alert>
          </v-card-text>
          <v-card-actions class="justify-center pa-8">
            <v-btn
              color="primary"
              size="x-large"
              block
              @click="handlePayment"
              :loading="loading"
            >
              Proceed to Payment
            </v-btn>
          </v-card-actions>
        </v-card>
        <v-alert v-else type="warning" class="mt-4">
          No plan selected. Please go back to the pricing page and choose a plan.
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { usePaymentStore } from '@/store/payment';
import { useRouter } from 'vue-router';

declare const Cashfree: any;

export default defineComponent({
  name: 'CheckoutView',
  setup() {
    const paymentStore = usePaymentStore();
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

    if (!selectedPlan.value) {
      router.push({ name: 'Pricing' });
    }

    return {
      selectedPlan,
      loading,
      error,
      handlePayment,
    };
  },
});
</script>
