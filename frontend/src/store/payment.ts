import { defineStore } from 'pinia';
import axios from 'axios';

interface PaymentState {
  orderId: string | null;
  amount: number | null;
  currency: string;
  status: string;
  paymentUrl: string | null;
  error: string | null;
  loading: boolean;
}

export const usePaymentStore = defineStore('payment', {
  state: (): PaymentState => ({
    orderId: null,
    amount: null,
    currency: 'INR',
    status: 'pending',
    paymentUrl: null,
    error: null,
    loading: false
  }),

  actions: {
    async createPayment(resumeFile: string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post('/api/create-payment', {
          resume_file: resumeFile,
          amount: 99.00,
          currency: 'INR'
        });
        
        this.orderId = response.data.order_id;
        this.paymentUrl = response.data.payment_url;
        this.status = response.data.status;
        
        // Open payment URL in new window if available
        if (this.paymentUrl) {
          window.open(this.paymentUrl, '_blank');
        }
        
        return response.data;
      } catch (error: any) {
        this.error = error.response?.data?.detail || 'Error creating payment';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async verifyPayment(orderId: string) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`/api/verify-payment/${orderId}`);
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
      this.currency = 'INR';
      this.status = 'pending';
      this.paymentUrl = null;
      this.error = null;
      this.loading = false;
    }
  }
});