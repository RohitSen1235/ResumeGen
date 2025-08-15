<template>
  <div class="d-flex justify-center">
    <v-btn
      @click="showTermsDialog = true"
      variant="text"
      :loading="loading"
      class="pa-0"
      style="height: auto; min-height: auto; max-width: 300px;"
    >
      <img 
        src="@/assets/Sign-In-Large---Active.png" 
        alt="Sign in with LinkedIn" 
        style="width: 100%; height: auto;"
      />
    </v-btn>

    <!-- Terms Agreement Dialog -->
    <v-dialog v-model="showTermsDialog" max-width="600" persistent>
      <v-card>
        <v-card-title class="text-h6 font-weight-bold">
          <v-icon icon="mdi-linkedin" class="mr-2" color="primary"></v-icon>
          LinkedIn Sign In - Terms Agreement
        </v-card-title>
        
        <v-card-text>
          <p class="text-body-1 mb-4">
            Before proceeding with LinkedIn sign in, you must agree to our terms and policies.
          </p>
          
          <v-checkbox
            v-model="termsAccepted"
            :rules="[v => !!v || 'You must agree to the terms to continue']"
            required
            density="comfortable"
            class="mb-2"
          >
            <template v-slot:label>
              <div class="text-body-2">
                I agree to the 
                <a href="/user-agreement" target="_blank" class="text-primary text-decoration-none">
                  User Agreement
                </a>, 
                <a href="/terms-of-service" target="_blank" class="text-primary text-decoration-none">
                  Terms of Service
                </a>, and 
                <a href="/privacy-policy" target="_blank" class="text-primary text-decoration-none">
                  Privacy Policy
                </a>
              </div>
            </template>
          </v-checkbox>

          <v-alert v-if="error" type="error" variant="tonal" class="mt-3" closable>
            {{ error }}
          </v-alert>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="cancelLinkedInLogin"
            :disabled="loading"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="proceedWithLinkedInLogin"
            :loading="loading"
            :disabled="!termsAccepted"
          >
            Continue with LinkedIn
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/store/auth'

const auth = useAuthStore()
const loading = ref(false)
const showTermsDialog = ref(false)
const termsAccepted = ref(false)
const error = ref('')

const cancelLinkedInLogin = () => {
  showTermsDialog.value = false
  termsAccepted.value = false
  error.value = ''
}

const proceedWithLinkedInLogin = async () => {
  if (!termsAccepted.value) {
    error.value = 'You must agree to the terms to continue'
    return
  }

  try {
    loading.value = true
    error.value = ''
    await auth.linkedinLogin()
    showTermsDialog.value = false
  } catch (err: any) {
    error.value = typeof err === 'string' ? err : 'LinkedIn login failed'
    console.error('LinkedIn login failed:', err)
  } finally {
    loading.value = false
  }
}
</script>
