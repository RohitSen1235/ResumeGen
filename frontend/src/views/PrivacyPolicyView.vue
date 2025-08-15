<template>
  <v-container class="privacy-policy-view" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row justify="center">
      <v-col cols="12" lg="10" xl="8">
        <v-card 
          class="pa-md-8 pa-4" 
          elevation="12" 
          rounded="xl" 
          style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.9);"
        >
          <v-card-title class="text-h4 font-weight-bold mb-6 text-grey-darken-3 text-center">
            <v-icon icon="mdi-shield-account" class="mr-3" color="primary"></v-icon>
            Privacy Policy
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

const privacyPolicyContent = `# Privacy Policy

**Last Updated:** August 15, 2025

## 1. Introduction

This Privacy Policy describes how we collect, use, store, and protect your personal information when you use our AI-powered resume customization service ("Service"). We are committed to protecting your privacy and handling your personal data transparently and securely.

## 2. Information We Collect

### 2.1 Personal Information You Provide
When you use our Service, you may provide us with:

- **Account Information:** Name, email address, username, and password
- **Profile Information:** Phone number, location, professional title, and career objectives
- **Resume Content:** Work experience, education, skills, achievements, and other professional information
- **Payment Information:** Billing address and payment method details (processed securely through third-party payment processors)
- **Communication Data:** Messages, feedback, and support requests you send to us

### 2.2 Information We Collect Automatically
When you use our Service, we automatically collect:

- **Usage Data:** How you interact with our Service, features used, and time spent
- **Device Information:** Device type, operating system, browser type, and IP address
- **Log Data:** Server logs, access times, and pages viewed
- **Cookies and Tracking Data:** Information collected through cookies and similar technologies

### 2.3 AI-Generated Content
We process the personal and professional information you provide to generate AI-powered resume suggestions and content recommendations.

## 3. How We Use Your Information

### 3.1 Primary Service Functions
We use your information to:

- Provide AI-powered resume customization and content generation
- Create personalized resume templates and suggestions
- Save and manage your resume drafts and versions
- Process payments for premium features
- Provide customer support and technical assistance

### 3.2 Service Improvement
We may use aggregated and anonymized data to:

- Improve our AI algorithms and content generation
- Enhance user experience and Service functionality
- Develop new features and capabilities
- Conduct analytics and research

### 3.3 Marketing and Promotional Communications
**We use your personal data for our own promotional and marketing purposes, including:**

- Sending you information about our products and services
- Notifying you about new features, updates, and improvements
- Sharing tips and best practices for resume writing and job searching
- Conducting surveys and gathering feedback about our Service

**Important:** We do **NOT** sell, rent, or share your personal data with third parties for their marketing purposes.

## 4. Data Sharing and Third Parties

### 4.1 No Sale or Sharing of Personal Data
**We do NOT sell, rent, lease, or share your personal data with third parties for commercial purposes.** This includes:

- Email addresses
- Phone numbers
- Physical addresses
- Any other personal information you provide

### 4.2 Limited Service Providers
We may share your information only with trusted service providers who help us operate our Service:

- **Payment Processors:** To process subscription payments securely
- **Cloud Storage Providers:** To store your data securely
- **Email Service Providers:** To send service-related communications
- **Analytics Providers:** To understand Service usage (using anonymized data only)

All service providers are contractually obligated to protect your data and use it only for specified purposes.

### 4.3 Legal Requirements
We may disclose your information when required by law or to:

- Comply with legal process or government requests
- Protect our rights, property, or safety
- Investigate potential violations of our terms
- Prevent fraud or abuse of our Service

## 5. Data Security and Protection

### 5.1 Security Measures
We implement industry-standard security measures to protect your personal data:

- **Encryption:** Data is encrypted in transit and at rest
- **Access Controls:** Strict access controls and authentication requirements
- **Regular Audits:** Periodic security assessments and vulnerability testing
- **Employee Training:** Staff training on data protection and privacy practices

### 5.2 Data Breach Response
In the event of a data breach that affects your personal information:

- We will notify affected users promptly as required by law
- We will provide information about what data was involved
- We will describe the steps we are taking to address the breach
- We will offer guidance on protective measures you can take

## 6. Data Retention

### 6.1 Active Accounts
We retain your personal information for as long as your account remains active and for the period necessary to provide our Service.

### 6.2 Account Deletion
When you delete your account:

- We will delete your personal information within 90 days
- Some information may be retained longer for legal compliance
- Anonymized usage data may be retained for service improvement
- Backup systems may retain data for up to 12 months for disaster recovery

### 6.3 Legal Retention Requirements
Some information may be retained longer to comply with:

- Legal obligations and regulatory requirements
- Tax and accounting record-keeping requirements
- Pending legal proceedings or investigations

## 7. Your Privacy Rights

### 7.1 Access and Portability
You have the right to:

- Access the personal information we have about you
- Receive a copy of your data in a portable format
- Request information about how we use your data

### 7.2 Correction and Updates
You may:

- Update your account information through your profile settings
- Request correction of inaccurate personal information
- Update your communication preferences

### 7.3 Deletion and Opt-Out Rights
You have the right to:

- Request deletion of your personal information
- Opt out of marketing communications
- Close your account at any time
- Withdraw consent for data processing where applicable

### 7.4 Marketing Communications
You can opt out of marketing communications by:

- Using the unsubscribe link in our emails
- Updating your preferences in your account settings
- Contacting us directly with your request

## 8. Cookies and Tracking Technologies

### 8.1 Types of Cookies We Use
- **Essential Cookies:** Required for basic Service functionality
- **Performance Cookies:** Help us understand how users interact with our Service
- **Preference Cookies:** Remember your settings and preferences

### 8.2 Cookie Management
You can control cookies through your browser settings:

- Most browsers allow you to refuse or accept cookies
- You can delete existing cookies from your browser
- Disabling essential cookies may limit Service functionality

## 9. International Data Transfers

If you are located outside our primary jurisdiction:

- We may transfer your data across borders for processing
- We ensure adequate protection through appropriate safeguards
- Transfers comply with applicable data protection laws
- We use standard contractual clauses or other approved mechanisms

## 10. Children's Privacy

Our Service is not intended for children under 18 years of age:

- We do not knowingly collect personal information from children under 18
- If we learn we have collected such information, we will delete it promptly
- Parents who believe their child has provided information may contact us

## 11. Third-Party Links and Services

Our Service may contain links to third-party websites or services:

- This Privacy Policy does not apply to third-party sites
- We are not responsible for third-party privacy practices
- We encourage you to review third-party privacy policies
- Third-party integrations are governed by their own terms

## 12. Updates to This Privacy Policy

### 12.1 Policy Changes
We may update this Privacy Policy from time to time:

- Material changes will be communicated via email or Service notification
- Minor updates may be posted with revised effective dates
- Continued use after changes constitutes acceptance of updated terms

### 12.2 Notification Methods
We will notify you of privacy policy changes through:

- Email notifications to your registered address
- Prominent notices within our Service
- Updates posted on our website

## 13. Legal Basis for Processing (EU/UK Users)

For users in the European Union and United Kingdom, we process personal data based on:

- **Contract Performance:** To provide our Service as requested
- **Legitimate Interests:** To improve our Service and communicate with users
- **Consent:** For marketing communications (where required by law)
- **Legal Compliance:** To meet regulatory and legal obligations

## 14. Contact Information and Requests

### 14.1 Privacy Questions
For questions about this Privacy Policy or our privacy practices, contact us at:

- **Email:** [privacy@company.com]
- **Address:** [Your Company Address]
- **Phone:** [Your Phone Number]

### 14.2 Data Subject Requests
To exercise your privacy rights or submit data subject requests:

- Use our online privacy request form at [URL]
- Email us at [privacy@company.com] with "Privacy Request" in the subject line
- Mail written requests to our address above

### 14.3 Response Timeframes
We will respond to privacy requests:

- Within 30 days for most requests
- Within 45 days for complex requests (with notification of extension)
- As required by applicable data protection laws

## 15. California Privacy Rights (CCPA)

California residents have additional rights under the California Consumer Privacy Act:

### 15.1 Right to Know
You have the right to know what personal information we collect, use, and share about you.

### 15.2 Right to Delete
You have the right to request deletion of your personal information, subject to certain exceptions.

### 15.3 Right to Opt-Out
You have the right to opt out of the sale of personal information (note: we do not sell personal information).

### 15.4 Non-Discrimination
We will not discriminate against you for exercising your privacy rights.

## 16. Effective Date and Acknowledgment

This Privacy Policy is effective as of August 15, 2025.

By using our Service, you acknowledge that:

- You have read and understood this Privacy Policy
- You consent to the collection, use, and processing of your personal information as described
- You understand your privacy rights and how to exercise them
- You agree to receive marketing communications about our own products and services (with opt-out options available)

## 17. Data Protection Officer

For privacy-related inquiries in jurisdictions that require a Data Protection Officer:

- **Email:** [dpo@company.com]
- **Address:** [DPO Address]

---

**This Privacy Policy represents our commitment to protecting your personal information and maintaining transparency about our data practices.**`

const formattedContent = computed(() => {
  return marked(privacyPolicyContent, { breaks: true })
})
</script>

<style scoped>
.privacy-policy-view {
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
  .privacy-policy-view {
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
