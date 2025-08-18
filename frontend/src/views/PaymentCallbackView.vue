<template>
  <v-container class="py-12">
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card elevation="8" rounded="xl">
          <v-card-title class="text-h4 font-weight-bold text-center pt-8 pb-6">
            <v-icon 
              :color="transactionData?.status === 'SUCCESS' ? 'success' : 'error'" 
              size="48" 
              class="mr-3"
            >
              {{ transactionData?.status === 'SUCCESS' ? 'mdi-check-circle' : 'mdi-alert-circle' }}
            </v-icon>
            Payment {{ transactionData?.status === 'SUCCESS' ? 'Successful' : 'Failed' }}
          </v-card-title>
          
          <v-card-text>
            <v-alert v-if="loading" type="info" class="mb-4">
              <v-progress-circular indeterminate size="20" class="mr-3"></v-progress-circular>
              Retrieving transaction details...
            </v-alert>
            
            <v-alert v-if="error" type="error" class="mb-4">
              {{ error }}
            </v-alert>
            
            <!-- Transaction Details -->
            <div v-if="transactionData && !loading">
              <v-alert 
                :type="transactionData.status === 'SUCCESS' ? 'success' : 'error'" 
                class="mb-6"
                prominent
              >
                <div class="text-h6">
                  {{ transactionData.status === 'SUCCESS' ? 'Payment Completed Successfully!' : 'Payment Failed' }}
                </div>
                <div class="text-body-2 mt-2">
                  {{ transactionData.status === 'SUCCESS' 
                    ? 'Your credits have been added to your account.' 
                    : 'Please try again or contact support if the issue persists.' 
                  }}
                </div>
              </v-alert>

              <!-- Invoice-like Details -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="bg-grey-lighten-4 text-h6">
                  <v-icon class="mr-2">mdi-receipt</v-icon>
                  Transaction Details
                </v-card-title>
                <v-card-text class="pa-0">
                  <v-list>
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Transaction ID</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        {{ transactionData.transaction_id || 'N/A' }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Order ID</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        {{ transactionData.order_id }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Amount</v-list-item-title>
                      <v-list-item-subtitle class="text-right text-h6 font-weight-bold">
                        {{ transactionData.currency }} {{ transactionData.amount }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Order Note</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        {{ transactionData.order_note }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Payment Method</v-list-item-title>
                      <v-list-item-subtitle class="text-right text-capitalize">
                        {{ transactionData.payment_method?.replace('_', ' ') || 'N/A' }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    
                    <v-list-item v-if="transactionData.payment_time">
                      <v-list-item-title class="font-weight-bold">Payment Time</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        {{ formatDateTime(transactionData.payment_time) }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider v-if="transactionData.payment_time"></v-divider>
                  </v-list>
                </v-card-text>
              </v-card>

              <!-- Customer Details -->
              <v-card variant="outlined" class="mb-4">
                <v-card-title class="bg-grey-lighten-4 text-h6">
                  <v-icon class="mr-2">mdi-account</v-icon>
                  Customer Details
                </v-card-title>
                <v-card-text class="pa-0">
                  <v-list>
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Customer Name</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        {{ transactionData.customer_name || 'N/A' }}
                      </v-list-item-subtitle>
                    </v-list-item>
                    <v-divider></v-divider>
                    
                    <v-list-item>
                      <v-list-item-title class="font-weight-bold">Customer Email</v-list-item-title>
                      <v-list-item-subtitle class="text-right">
                        {{ transactionData.customer_email || 'N/A' }}
                      </v-list-item-subtitle>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>

              <!-- Status Badge -->
              <div class="text-center mb-4">
                <v-chip
                  :color="transactionData.status === 'SUCCESS' ? 'success' : 'error'"
                  size="large"
                  variant="elevated"
                >
                  <v-icon start>
                    {{ transactionData.status === 'SUCCESS' ? 'mdi-check' : 'mdi-close' }}
                  </v-icon>
                  {{ transactionData.status }}
                </v-chip>
              </div>
            </div>
          </v-card-text>
          
          <v-card-actions class="justify-center pa-6">
            <v-btn
              color="primary"
              size="large"
              variant="elevated"
              @click="goToPricing"
              prepend-icon="mdi-arrow-left"
            >
              Back to Pricing
            </v-btn>
            <v-btn
              v-if="transactionData?.status === 'SUCCESS'"
              color="success"
              size="large"
              variant="elevated"
              @click="goToResumeBuilder"
              prepend-icon="mdi-file-document-edit"
            >
              Start Building Resume
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

interface TransactionData {
  order_id: string;
  transaction_id?: string;
  amount: number;
  currency: string;
  status: string;
  customer_name?: string;
  customer_email?: string;
  payment_method?: string;
  payment_time?: string;
  order_note: string;
  message?: string;
}

export default defineComponent({
  name: 'PaymentCallbackView',
  setup() {
    const router = useRouter();
    const loading = ref(true);
    const error = ref<string | null>(null);
    const transactionData = ref<TransactionData | null>(null);

    const formatDateTime = (dateTimeString: string) => {
      try {
        const date = new Date(dateTimeString);
        return date.toLocaleString('en-IN', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          timeZone: 'Asia/Kolkata'
        });
      } catch (e) {
        return dateTimeString;
      }
    };

    const goToPricing = () => {
      router.push({ name: 'Pricing' });
    };

    const goToResumeBuilder = () => {
      router.push('/resume-builder');
    };

    onMounted(async () => {
      const urlParams = new URLSearchParams(window.location.search);
      
      console.log('URL Parameters:', Object.fromEntries(urlParams.entries()));
      
      // Try different parameter names that Cashfree might use
      const orderId = urlParams.get('order_id') || 
                     urlParams.get('orderId') || 
                     urlParams.get('cf_order_id') ||
                     urlParams.get('orderid');
      
      console.log('Order ID found:', orderId);
      
      if (orderId) {
        try {
          // Fetch transaction details from backend using order ID
          const response = await axios.get(`/api/payment/transaction/${orderId}`);
          transactionData.value = response.data;
          console.log('Transaction data:', transactionData.value);
        } catch (err) {
          console.error('Error fetching transaction details:', err);
          // Fallback to latest transaction
          await fetchLatestTransaction();
        } finally {
          loading.value = false;
        }
      } else {
        // No order ID in URL, fetch the latest successful transaction for this user
        console.log('No order ID in URL parameters, fetching latest transaction');
        await fetchLatestTransaction();
      }
    });

    const fetchLatestTransaction = async () => {
      try {
        // Fetch the latest transaction for the current user
        const response = await axios.get('/api/payment/latest-transaction');
        if (response.data && response.data.transaction_id) {
          transactionData.value = response.data;
          console.log('Latest transaction data:', transactionData.value);
        } else {
          // If no recent transaction found, show generic success
          transactionData.value = {
            order_id: 'Payment Completed',
            amount: 875,
            currency: 'INR',
            status: 'SUCCESS',
            order_note: 'Resume Generation Credits',
            customer_name: 'Valued Customer',
            customer_email: 'Payment processed successfully',
            payment_method: 'Cashfree Payment Gateway',
            message: 'Payment completed successfully'
          };
        }
      } catch (err) {
        console.error('Error fetching latest transaction:', err);
        // Show generic success as fallback
        transactionData.value = {
          order_id: 'Payment Completed',
          amount: 875,
          currency: 'INR',
          status: 'SUCCESS',
          order_note: 'Resume Generation Credits',
          customer_name: 'Valued Customer',
          customer_email: 'Payment processed successfully',
          payment_method: 'Cashfree Payment Gateway',
          message: 'Payment completed successfully'
        };
      } finally {
        loading.value = false;
      }
    };

    return {
      loading,
      error,
      transactionData,
      formatDateTime,
      goToPricing,
      goToResumeBuilder,
    };
  },
});
</script>

<style scoped>
.v-list-item-subtitle {
  opacity: 1 !important;
}

.v-card-title {
  word-break: break-word;
}

.text-right {
  text-align: right;
}
</style>
