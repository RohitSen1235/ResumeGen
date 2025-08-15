<template>
  <v-container class="user-agreement-view" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row justify="center">
      <v-col cols="12" lg="10" xl="8">
        <v-card 
          class="pa-md-8 pa-4" 
          elevation="12" 
          rounded="xl" 
          style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.9);"
        >
          <v-card-title class="text-h4 font-weight-bold mb-6 text-grey-darken-3 text-center">
            <v-icon icon="mdi-handshake" class="mr-3" color="primary"></v-icon>
            User Agreement
          </v-card-title>
          
          <v-card-text class="pa-0">
            <div class="markdown-content" v-html="formattedContent"></div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'

const userAgreementContent = `# User Agreement

**Last Updated:** August 15, 2025

## 1. Introduction

This User Agreement ("Agreement") governs your use of our AI-powered resume customization service. By creating an account or using our Service, you agree to comply with and be bound by the terms and conditions set forth in this Agreement.

## 2. Eligibility and Account Creation

### 2.1 Eligibility
- You must be at least 18 years old to use our Service
- You must have the legal capacity to enter into contracts
- You represent that all information provided during registration is accurate and complete

### 2.2 Account Security
- You are responsible for maintaining the confidentiality of your account credentials
- You agree to notify us immediately of any unauthorized access to your account
- You are solely responsible for all activities that occur under your account

## 3. Service Description and AI Content Disclaimer

### 3.1 Service Overview
Our Service provides AI-powered tools to help you create, customize, and improve your resume through automated content generation and suggestions.

### 3.2 Critical AI Content Disclaimer
**YOU ACKNOWLEDGE AND UNDERSTAND:**

- **AI-generated content may contain inaccuracies, errors, or content that does not accurately reflect your actual experience**
- **The responsibility lies entirely with you to verify, review, and correct all AI-generated content**
- **AI-generated content is provided as guidance and inspiration only, not as factual statements**
- **You must ensure all final resume content accurately represents your qualifications and experience**
- **We provide review and editing functionality specifically for you to verify and modify AI content**

### 3.3 Professional Responsibility
- You agree that AI-generated suggestions should never be used without human review and verification
- You understand that employers expect accurate information on resumes
- You acknowledge that submitting false information to employers may have serious professional consequences

## 4. User Obligations and Prohibited Activities

### 4.1 Permitted Use
You may use our Service to:
- Generate resume content suggestions and templates
- Customize and edit resume formats and layouts
- Review and modify AI-generated content to ensure accuracy
- Create multiple versions of your resume for different applications

### 4.2 Prohibited Activities
You agree NOT to:
- Submit false or misleading information about your background
- Use AI-generated content without proper review and verification
- Create resumes containing fraudulent qualifications or experiences
- Use the Service to infringe on others' intellectual property rights
- Attempt to reverse engineer or copy our software
- Use the Service for any illegal or unethical purposes

## 5. Employment Outcome Disclaimer

### 5.1 No Guarantee of Employment Success
**IMPORTANT EMPLOYMENT DISCLAIMER:**

Our company **EXPRESSLY DISCLAIMS LIABILITY** for:
- **Interview rejections or lack of interview invitations**
- **Unsuccessful job applications**
- **Employment termination or job loss of any kind**
- **Career setbacks or professional difficulties**
- **Hiring decisions made by employers, recruiters, or HR departments**

### 5.2 Factors Beyond Our Control
You acknowledge that employment outcomes depend on numerous factors including:
- Market conditions and economic factors
- Competition from other candidates
- Employer preferences and requirements
- Your interview performance and soft skills
- Industry trends and demand
- Geographic and timing considerations

### 5.3 Resume as One Component
You understand that a resume is only one element of the job application process, and employers make hiring decisions based on multiple factors beyond resume content.

## 6. Intellectual Property and Content Ownership

### 6.1 Your Content
- You retain ownership of personal information and content you provide
- You grant us a limited license to use your content solely to provide our Service
- You may delete your content or close your account at any time

### 6.2 AI-Generated Content
- You receive a license to use AI-generated content in your personal resumes
- AI-generated content becomes part of your resume once you review and approve it
- You assume full responsibility for any AI-generated content you choose to use

### 6.3 Service Technology
- Our software, algorithms, and technology remain our intellectual property
- You receive only a limited license to use our Service as intended
- You may not copy, distribute, or create derivative works based on our technology

## 7. Data Privacy and Personal Information

Your privacy is important to us. Please review our Privacy Policy, which is incorporated into this Agreement by reference, to understand:
- How we collect and use your personal information
- Your rights regarding your personal data
- Our data security and retention practices
- Third-party integrations and data sharing

## 8. Service Modifications and Availability

### 8.1 Service Changes
- We reserve the right to modify, update, or discontinue features of our Service
- We will provide reasonable notice of material changes when possible
- Continued use of the Service after changes constitutes acceptance

### 8.2 Service Availability
- We strive to maintain high service availability but do not guarantee uninterrupted access
- We are not liable for temporary service outages or technical difficulties
- We may perform scheduled maintenance that temporarily limits service access

## 9. Payment Terms and Subscriptions

### 9.1 Subscription Services
- Certain features may require paid subscriptions
- Subscription fees are billed according to your selected plan
- You authorize us to charge your payment method for subscription fees

### 9.2 Refund Policy
- Refunds are provided according to our published refund policy
- We reserve the right to modify pricing with reasonable advance notice
- You may cancel your subscription at any time through your account settings

## 10. Disclaimers and Limitation of Liability

### 10.1 Service Disclaimers
TO THE MAXIMUM EXTENT PERMITTED BY LAW:
- Our Service is provided "AS IS" and "AS AVAILABLE"
- We disclaim all warranties, express or implied
- We do not warrant that our Service will meet your specific needs or expectations
- We do not guarantee the accuracy or completeness of AI-generated content

### 10.2 Limitation of Liability
**OUR LIABILITY IS LIMITED AS FOLLOWS:**
- We shall not be liable for indirect, incidental, special, or consequential damages
- Our maximum liability shall not exceed the fees you paid in the 12 months prior to the claim
- This limitation applies to all claims, regardless of legal theory
- Some jurisdictions may not allow these limitations, so they may not apply to you

## 11. Indemnification

You agree to defend, indemnify, and hold us harmless from claims, damages, or expenses arising from:
- Your use of the Service or violation of this Agreement
- Content you submit or information you provide
- Your employment activities or professional conduct
- Any third-party claims related to your use of our Service

## 12. Termination

### 12.1 Termination by You
- You may terminate your account at any time
- Upon termination, you lose access to our Service
- You may request deletion of your personal data subject to our retention policies

### 12.2 Termination by Us
- We may terminate accounts for violation of this Agreement
- We may suspend accounts pending investigation of suspected violations
- We reserve the right to terminate Service with reasonable notice

## 13. Dispute Resolution and Governing Law

### 13.1 Governing Law
This Agreement shall be governed by and construed in accordance with the laws of [Your Jurisdiction], without regard to conflict of law principles.

### 13.2 Dispute Resolution
- Disputes shall be resolved through binding arbitration
- Arbitration shall be conducted on an individual basis, not as a class action
- You may opt out of arbitration within 30 days of agreeing to these terms

## 14. General Provisions

### 14.1 Entire Agreement
This Agreement, together with our Privacy Policy and any additional terms, constitutes the entire agreement between you and us.

### 14.2 Severability
If any provision is deemed invalid or unenforceable, the remaining provisions shall remain in full force and effect.

### 14.3 Assignment
You may not assign your rights under this Agreement. We may assign our rights with reasonable notice.

### 14.4 Updates to Agreement
We may update this Agreement from time to time. Material changes will be communicated through our Service or via email.

## 15. Contact Information

For questions about this User Agreement, please contact us at:
- Email: [your-email@company.com]
- Address: [Your Company Address]
- Phone: [Your Phone Number]

## 16. Acknowledgment

**By using our Service, you acknowledge that:**
- You have read and understood this Agreement
- You agree to be bound by all terms and conditions
- You understand the limitations and disclaimers regarding AI-generated content
- You accept full responsibility for verifying and editing all AI-generated content
- You understand that we are not liable for employment outcomes or career results

**This Agreement is effective as of the date you first use our Service or create an account.**`

const formattedContent = computed(() => {
  return marked(userAgreementContent, { breaks: true })
})
</script>

<style scoped>
.user-agreement-view {
  min-height: 100vh;
  padding: 24px 0;
}

.markdown-content {
  background-color: white;
  padding: 32px;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
  line-height: 1.8;
  font-size: 0.95rem;
  max-height: 80vh;
  overflow-y: auto;
}

/* Markdown styling */
.markdown-content :deep(h1) {
  color: #1976d2;
  font-size: 2.2rem;
  font-weight: 700;
  margin: 0 0 24px 0;
  padding-bottom: 12px;
  border-bottom: 3px solid #1976d2;
}

.markdown-content :deep(h2) {
  color: #1565c0;
  font-size: 1.6rem;
  font-weight: 600;
  margin: 32px 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e3f2fd;
}

.markdown-content :deep(h3) {
  color: #1976d2;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 24px 0 12px 0;
}

.markdown-content :deep(h4) {
  color: #424242;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 20px 0 10px 0;
}

.markdown-content :deep(p) {
  margin: 12px 0;
  color: #424242;
  text-align: justify;
}

.markdown-content :deep(ul), 
.markdown-content :deep(ol) {
  margin: 16px 0;
  padding-left: 24px;
}

.markdown-content :deep(li) {
  margin: 8px 0;
  color: #424242;
}

.markdown-content :deep(strong) {
  color: #1976d2;
  font-weight: 600;
}

.markdown-content :deep(em) {
  color: #666;
  font-style: italic;
}

.markdown-content :deep(code) {
  background-color: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #1976d2;
  margin: 16px 0;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-radius: 0 8px 8px 0;
}

.markdown-content :deep(hr) {
  border: none;
  height: 2px;
  background: linear-gradient(to right, #1976d2, #e3f2fd, #1976d2);
  margin: 32px 0;
  border-radius: 1px;
}

/* Custom scrollbar */
.markdown-content::-webkit-scrollbar {
  width: 8px;
}

.markdown-content::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 4px;
}

.markdown-content::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-primary), 0.5);
  border-radius: 4px;
}

.markdown-content::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-primary), 0.7);
}

/* Mobile responsiveness */
@media (max-width: 960px) {
  .markdown-content {
    padding: 20px;
    font-size: 0.9rem;
    max-height: 75vh;
  }
  
  .markdown-content :deep(h1) {
    font-size: 1.8rem;
  }
  
  .markdown-content :deep(h2) {
    font-size: 1.4rem;
  }
  
  .markdown-content :deep(h3) {
    font-size: 1.2rem;
  }
}

@media (max-width: 600px) {
  .user-agreement-view {
    padding: 12px 0;
  }
  
  .markdown-content {
    padding: 16px;
    font-size: 0.85rem;
    max-height: 70vh;
  }
  
  .markdown-content :deep(h1) {
    font-size: 1.6rem;
  }
  
  .markdown-content :deep(h2) {
    font-size: 1.3rem;
  }
  
  .markdown-content :deep(h3) {
    font-size: 1.1rem;
  }
}
</style>
