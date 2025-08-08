import { defineStore } from 'pinia';
import axios from 'axios';
import { useAuthStore } from './auth';

const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_BACKEND_URL}`
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`;
  }
  return config;
});

interface PaymentState {
  orderId: string | null;
  amount: number | null;
  currency: string;
  status: string;
  paymentUrl: string | null;
  clientSecret: string | null;
  error: string | null;
  loading: boolean;
}

export const usePaymentStore = defineStore('payment', {
  state: (): PaymentState => ({
    orderId: null,
    amount: null,
    currency: 'USD',
    status: 'pending',
    paymentUrl: null,
    clientSecret: null,
    error: null,
    loading: false
  }),

  actions: {
    async fetchProductDetails() {
      try {
        this.loading = true;
        this.error = null;
        const response = await apiClient.get('/payment/product-details');
        if (!response.data?.amount) {
          throw new Error('Invalid product details response');
        }
        return response.data;
      } catch (error: any) {
        console.error('Error fetching product details:', error);
        this.error = error.response?.data?.detail || 'Failed to load product details';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createPaymentIntent(amount: number) {
      this.loading = true;
      this.error = null;
      try {
        console.log('Payment store: Creating payment intent...');
        console.log('API base URL:', import.meta.env.VITE_BACKEND_URL);
        
        const response = await apiClient.post('/payment/create-intent', { amount });
        
        console.log('Payment store: Response received:', response.data);
        this.clientSecret = response.data.clientSecret;
        this.amount = amount;
        return response.data;
      } catch (error: any) {
        console.error('Payment store: Error creating payment intent:', error);
        console.error('Payment store: Error response:', error.response);
        this.error = error.response?.data?.detail || 'Error creating payment intent';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    setError(message: string) {
      this.error = message;
    },

    async verifyPayment(orderId: string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get(`/verify-payment/${orderId}`);
        this.status = response.data.status;
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Error verifying payment';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    resetPayment() {
      this.orderId = null;
      this.amount = null;
      this.currency = 'USD';
      this.status = 'pending';
      this.paymentUrl = null;
      this.clientSecret = null;
      this.error = null;
      this.loading = false;
    }
  }
});
