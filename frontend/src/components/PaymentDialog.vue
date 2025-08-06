<template>
  <v-dialog :model-value="dialog" @update:model-value="dialog = $event" persistent max-width="500">
    <v-card>
      <v-card-title class="text-h5">
        Purchase Credits
      </v-card-title>

      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12">
              <!-- Loading overlay for payment confirmation -->
              <div v-if="loading && paymentInitiated" class="text-center mb-4">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
                <div class="mt-3">Processing payment...</div>
              </div>

              <!-- Loading for initial setup -->
              <div v-else-if="loading && !paymentInitiated" class="text-center">
                <v-progress-circular indeterminate color="primary"></v-progress-circular>
                <div class="mt-3">Initializing payment...</div>
              </div>

              <div v-if="error" class="text-error mb-4">
                {{ error }}
              </div>

              <div v-if="!paymentInitiated && !loading">
                <p class="mb-4">To generate resumes, you need credits. Purchase 10 credits for $9.00:</p>
                <p>Current Credits: {{ credits }}</p>
                <div class="d-flex justify-space-between align-center mb-4">
                  <span class="text-h6">Amount:</span>
                  <span class="text-h6">$9.00</span>
                </div>
              </div>
              
              <div v-if="paymentInitiated && paymentStatus !== 'completed'">
                <div id="payment-element" class="mb-4"></div>
              </div>

              <div v-if="paymentStatus === 'completed'">
                <v-alert
                  type="success"
                  class="mb-4"
                >
                  Payment successful! Your credits have been added to your account.
                </v-alert>
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        
        <v-btn
          color="grey darken-1"
          variant="text"
          @click="closeDialog"
          :disabled="loading"
        >
          Close
        </v-btn>

        <v-btn
          v-if="!paymentInitiated"
          color="orange-lighten-2"
          @click="initiatePayment"
          :loading="loading"
          :disabled="loading"
        >
          Purchase Credits
        </v-btn>

        <v-btn
          v-else-if="paymentInitiated && paymentStatus !== 'completed'"
          color="orange-lighten-2"
          @click="confirmPayment"
          :loading="loading"
          :disabled="loading"
        >
          Complete Payment
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, nextTick } from 'vue';
import { usePaymentStore } from '@/store/payment';
import axios from 'axios';

declare global {
  interface Window {
    Stripe: any;
  }
}

export default defineComponent({
  name: 'PaymentDialog',

  props: {
    modelValue: {
      type: Boolean,
      required: true
    },
    resumeFile: {
      type: String,
      required: true,
      validator: (value: string | null): boolean => {
        return value !== null;
      }
    },
    credits: {
      type: Number,
      required: true
    }
  },

  data() {
    return {
      localCredits: this.credits
    }
  },

  methods: {
    purchaseCredits() {
      axios.post('/purchase-credits', {
        amount: 10
      })
      .then(response => {
        this.localCredits = response.data.credits;
      })
      .catch(error => {
        console.error('Error purchasing credits:', error);
      });
    }
  },

  emits: ['update:modelValue', 'payment-completed'],

  setup(props, { emit }) {
    const paymentStore = usePaymentStore();
    const paymentInitiated = ref(false);
    const amount = ref(99.00);
    const checkStatusInterval = ref<number | null>(null);

    const dialog = computed({
      get: () => props.modelValue,
      set: (value) => emit('update:modelValue', value)
    });

    const loading = computed(() => paymentStore.loading);
    const error = computed(() => paymentStore.error);
    const paymentStatus = computed(() => paymentStore.status);

    const alertType = computed(() => {
      switch (paymentStore.status) {
        case 'completed':
          return 'success';
        case 'failed':
          return 'error';
        default:
          return 'info';
      }
    });

    const statusMessage = computed(() => {
      switch (paymentStore.status) {
        case 'completed':
          return 'Payment successful! You can now download your resume.';
        case 'failed':
          return 'Payment failed. Please try again.';
        default:
          return 'Payment is being processed. Please wait or click "Check Status" to verify.';
      }
    });

    const stripe = ref<any>(null);
    const elements = ref<any>(null);
    const clientSecret = ref<string>('');

    onMounted(async () => {
      stripe.value = window.Stripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);
    });

    const initiatePayment = async () => {
      try {
        console.log('Starting payment initiation...');
        console.log('Stripe object:', stripe.value);
        console.log('Stripe public key:', import.meta.env.VITE_STRIPE_PUBLIC_KEY);
        
        if (!stripe.value) {
          console.error('Stripe not initialized - stripe.value is null');
          throw new Error('Stripe not initialized');
        }

        console.log('Creating payment intent...');
        // Create payment intent via store
        await paymentStore.createPaymentIntent();
        console.log('Payment intent created, client secret:', paymentStore.clientSecret);
        
        if (!paymentStore.clientSecret) {
          console.error('No client secret received from backend');
          throw new Error('Failed to get client secret');
        }
        
        console.log('Initializing Stripe Elements...');
        // Initialize Stripe Elements
        elements.value = stripe.value.elements({
          clientSecret: paymentStore.clientSecret,
          appearance: {
            theme: 'stripe',
            variables: {
              colorPrimary: '#ff9800',
              colorBackground: '#ffffff',
              colorText: '#30313d',
            }
          }
        });

        console.log('Setting paymentInitiated to true...');
        paymentInitiated.value = true;
        
        // Wait for Vue to update the DOM
        await nextTick();
        
        console.log('Creating payment element...');
        const paymentElement = elements.value.create('payment');
        console.log('Mounting payment element...');
        await paymentElement.mount('#payment-element');
        
        console.log('Payment initialization successful');
      } catch (err) {
        const error = err as Error;
        console.error('Payment initiation failed:', error);
        console.error('Error details:', {
          message: error.message,
          stack: error.stack,
          paymentStoreError: paymentStore.error
        });
        paymentStore.setError('Failed to initialize payment: ' + error.message);
      }
    };

    const confirmPayment = async () => {
      try {
        console.log('Starting payment confirmation...');
        console.log('Stripe object:', stripe.value);
        console.log('Elements object:', elements.value);
        
        if (!stripe.value || !elements.value) {
          throw new Error('Stripe not initialized');
        }

        // Check if payment element is still mounted
        const paymentElementDiv = document.getElementById('payment-element');
        console.log('Payment element div:', paymentElementDiv);
        
        if (!paymentElementDiv) {
          throw new Error('Payment element not found in DOM');
        }

        paymentStore.loading = true;
        
        console.log('Calling stripe.confirmPayment...');
        const { error } = await stripe.value.confirmPayment({
          elements: elements.value,
          confirmParams: {
            return_url: window.location.origin + '/payment-success',
          }
        });

        if (error) {
          console.error('Stripe confirmPayment error:', error);
          throw error;
        }

        console.log('Payment confirmation successful');
        // Payment succeeded
        paymentStore.status = 'completed';
        emit('payment-completed');
      } catch (err) {
        const error = err as Error;
        console.error('Payment confirmation failed:', error);
        console.error('Error details:', {
          message: error.message,
          stack: error.stack,
          paymentStoreError: paymentStore.error
        });
        paymentStore.setError('Payment confirmation failed: ' + error.message);
      } finally {
        paymentStore.loading = false;
      }
    };

    const checkPaymentStatus = async () => {
      if (!paymentStore.orderId) return;
      
      try {
        const result = await paymentStore.verifyPayment(paymentStore.orderId);
        if (result.status === 'completed') {
          stopStatusCheck();
          emit('payment-completed');
        }
      } catch (error) {
        console.error('Payment status check failed:', error);
      }
    };

    const startStatusCheck = () => {
      if (checkStatusInterval.value) return;
      
      // Check status every 5 seconds
      checkStatusInterval.value = window.setInterval(() => {
        if (paymentStore.status === 'pending') {
          checkPaymentStatus();
        } else {
          stopStatusCheck();
        }
      }, 5000);
    };

    const stopStatusCheck = () => {
      if (checkStatusInterval.value) {
        clearInterval(checkStatusInterval.value);
        checkStatusInterval.value = null;
      }
    };

    const downloadResume = async () => {
      try {
        const response = await axios.get(`${props.resumeFile}`, {
          responseType: 'blob'
        });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', props.resumeFile);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (error) {
        console.error('Download failed:', error);
      }
    };

    const closeDialog = () => {
      stopStatusCheck();
      if (paymentStatus.value !== 'pending') {
        paymentStore.resetPayment();
        paymentInitiated.value = false;
      }
      dialog.value = false;
    };

    return {
      dialog,
      loading,
      error,
      amount,
      paymentInitiated,
      paymentStatus,
      statusMessage,
      alertType,
      initiatePayment,
      confirmPayment,
      checkPaymentStatus,
      downloadResume,
      closeDialog
    };
  }
});
</script>
