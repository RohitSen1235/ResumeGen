<template>
  <v-dialog :model-value="dialog" @update:model-value="dialog = $event" persistent max-width="500">
    <v-card>
      <v-card-title class="text-h5">
        Resume Payment
      </v-card-title>

      <v-card-text>
        <v-container>
          <v-row v-if="loading">
            <v-col cols="12" class="text-center">
              <v-progress-circular indeterminate color="primary"></v-progress-circular>
              <div class="mt-3">Processing payment...</div>
            </v-col>
          </v-row>

          <v-row v-else>
            <v-col cols="12">
              <div v-if="error" class="error--text mb-4">
                {{ error }}
              </div>

              <div v-if="!paymentInitiated">
                <p class="mb-4">To download your customized resume, please complete the payment:</p>
                <div class="d-flex justify-space-between align-center mb-4">
                  <span class="text-h6">Amount:</span>
                  <span class="text-h6">₹{{ amount }}</span>
                </div>
              </div>

              <div v-else>
                <v-alert
                  :type="alertType"
                  class="mb-4"
                >
                  {{ statusMessage }}
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
          color="primary"
          @click="initiatePayment"
          :loading="loading"
          :disabled="loading"
        >
          Pay Now
        </v-btn>

        <v-btn
          v-else-if="paymentStatus === 'pending'"
          color="primary"
          @click="checkPaymentStatus"
          :loading="loading"
          :disabled="loading"
        >
          Check Status
        </v-btn>

        <v-btn
          v-else-if="paymentStatus === 'completed'"
          color="success"
          @click="downloadResume"
          :loading="loading"
          :disabled="loading"
        >
          Download Resume
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { usePaymentStore } from '@/store/payment';
import axios from 'axios';

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

    const initiatePayment = async () => {
      try {
        await paymentStore.createPayment(props.resumeFile);
        paymentInitiated.value = true;
        startStatusCheck();
      } catch (error) {
        console.error('Payment initiation failed:', error);
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
        const response = await axios.get(`http://localhost:8000${props.resumeFile}`, {
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
      checkPaymentStatus,
      downloadResume,
      closeDialog
    };
  }
});
</script>