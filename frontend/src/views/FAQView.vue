<template>
  <v-container class="faq-view" fluid style="background: linear-gradient(to top right, #E3F2FD, #BBDEFB);">
    <v-row justify="center">
      <v-col cols="12" lg="10" xl="8">
        <v-card 
          class="pa-md-8 pa-4" 
          elevation="12" 
          rounded="xl" 
          style="backdrop-filter: blur(10px); background-color: rgba(255, 255, 255, 0.9);"
        >
          <v-card-title class="text-h4 font-weight-bold mb-6 text-grey-darken-3 text-center">
            <v-icon icon="mdi-help-circle" class="mr-3" color="primary"></v-icon>
            Frequently Asked Questions
          </v-card-title>
          
          <v-card-text class="pa-0">
            <div class="faq-content">
              <v-expansion-panels variant="accordion" multiple>
                <v-expansion-panel
                  v-for="(faq, index) in faqs"
                  :key="index"
                  :title="faq.question"
                  elevation="2"
                  rounded="lg"
                  class="mb-3"
                >
                  <v-expansion-panel-text>
                    <div class="faq-answer" v-html="faq.answer"></div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { marked } from 'marked'

interface FAQ {
  question: string
  answer: string
}

const faqs = ref<FAQ[]>([
  {
    question: "What is ResumeGenie and how does it work?",
    answer: marked(`ResumeGenie is an AI-powered resume customization service that helps you create professional, tailored resumes for specific job applications. 

**How it works:**
- Upload your existing resume or create one from scratch
- Paste the job description you're applying for
- Our AI analyzes both documents and generates optimized content
- Review and edit the AI suggestions to ensure accuracy
- Download your customized resume in PDF or Word format`) as string
  },
  {
    question: "Is the AI-generated content accurate?",
    answer: marked(`**Important:** AI-generated content is provided as **suggestions and guidance only**. 

**You are responsible for:**
- Reviewing all AI-generated content carefully
- Verifying that all information accurately reflects your experience
- Editing and customizing content to match your actual qualifications
- Ensuring all final resume content is truthful and accurate

The AI helps with formatting, wording, and optimization, but you must ensure the content represents your real experience.`) as string
  },
  {
    question: "What file formats can I upload and download?",
    answer: marked(`**Upload formats supported:**
- PDF files
- Microsoft Word documents (.docx)
- Plain text files

**Download formats available:**
- PDF (recommended for job applications)
- Microsoft Word (.docx) for further editing

All downloads maintain professional formatting and are ATS (Applicant Tracking System) compatible.`) as string
  },
  {
    question: "How much does ResumeGenie cost?",
    answer: marked(`We offer flexible pricing options:

**Free Tier:**
- Basic resume analysis
- Limited AI suggestions
- Standard templates

**Premium Plans:**
- Unlimited resume customizations
- Advanced AI optimization
- Premium templates
- Priority support
- Multiple download formats

Check our [Pricing](/pricing) page for current rates and features.`) as string
  },
  {
    question: "Is my personal information secure?",
    answer: marked(`**Yes, we take your privacy seriously:**

- All data is encrypted in transit and at rest
- We never sell or share your personal information
- Your resume content is only used to provide our service
- You can delete your account and data at any time
- We comply with data protection regulations

Read our [Privacy Policy](/privacy-policy) for complete details.`) as string
  },
  {
    question: "Can ResumeGenie guarantee I'll get job interviews?",
    answer: marked(`**No, we cannot guarantee employment outcomes.**

**Important disclaimer:**
- We are not liable for interview rejections or unsuccessful applications
- Employment decisions depend on many factors beyond your resume
- Your resume is just one component of the job application process
- Market conditions, competition, and employer preferences all play a role

Our service helps optimize your resume, but success depends on multiple factors including your qualifications, interview skills, and market conditions.`) as string
  },
  {
    question: "What types of jobs and industries does ResumeGenie support?",
    answer: marked(`ResumeGenie works for virtually any industry and job level:

**Industries:**
- Technology and Software
- Healthcare and Medical
- Finance and Banking
- Marketing and Sales
- Education and Academia
- Engineering and Manufacturing
- And many more...

**Job Levels:**
- Entry-level positions
- Mid-career professionals
- Senior and executive roles
- Career changers
- Recent graduates`) as string
  },
  {
    question: "How do I edit the AI-generated content?",
    answer: marked(`**Easy editing process:**

1. **Review Phase:** Carefully read all AI-generated suggestions
2. **Edit Mode:** Click the "Edit" button in the preview section
3. **Make Changes:** Modify content to accurately reflect your experience
4. **Save Changes:** Save your edits before downloading
5. **Final Review:** Double-check everything before submitting to employers

**Remember:** Always ensure the final content truthfully represents your qualifications and experience.`) as string
  },
  {
    question: "What if I'm not satisfied with the results?",
    answer: marked(`**We want you to be satisfied:**

- Try different job descriptions for varied results
- Use the edit feature to customize AI suggestions
- Experiment with different resume templates
- Contact our support team for assistance

**Refund Policy:**
- Check our refund policy for premium subscriptions
- We offer support to help optimize your results
- Remember that AI suggestions are starting points for customization`) as string
  },
  {
    question: "How do I contact support?",
    answer: marked(`**Get help when you need it:**

**Email Support:** [support@ResumeGenie.com]
**Response Time:** Within 24 hours for most inquiries

**Before contacting support:**
- Check this FAQ for common questions
- Try the edit feature to customize results
- Review our user guides and tutorials

**Include in your message:**
- Description of the issue
- Steps you've already tried
- Your account email (if applicable)`) as string
  },
  {
    question: "Can I use ResumeGenie for multiple job applications?",
    answer: marked(`**Absolutely! That's what we're designed for:**

- Create multiple customized versions of your resume
- Tailor each version for specific job applications
- Save different versions for different industries
- Premium users get unlimited customizations

**Best Practice:**
Customize your resume for each job application by using the specific job description to generate targeted content.`) as string
  },
  {
    question: "Is ResumeGenie compatible with Applicant Tracking Systems (ATS)?",
    answer: marked(`**Yes, our resumes are ATS-optimized:**

**ATS-Friendly Features:**
- Clean, simple formatting
- Standard fonts and layouts
- Proper heading structure
- Keyword optimization
- Compatible file formats

**What this means:**
- Your resume can be properly parsed by ATS software
- Important information won't be lost in automated screening
- Better chances of passing initial automated reviews`) as string
  }
])
</script>

<style scoped>
.faq-view {
  min-height: 100vh;
  padding: 24px 0;
}

.faq-content {
  max-height: 80vh;
  overflow-y: auto;
}

.faq-answer {
  line-height: 1.7;
  font-size: 0.95rem;
}

/* Markdown styling for FAQ answers */
.faq-answer :deep(h1),
.faq-answer :deep(h2),
.faq-answer :deep(h3),
.faq-answer :deep(h4) {
  color: #1976d2;
  font-weight: 600;
  margin: 16px 0 8px 0;
}

.faq-answer :deep(p) {
  margin: 12px 0;
  color: #424242;
}

.faq-answer :deep(ul),
.faq-answer :deep(ol) {
  margin: 12px 0;
  padding-left: 20px;
}

.faq-answer :deep(li) {
  margin: 6px 0;
  color: #424242;
}

.faq-answer :deep(strong) {
  color: #1976d2;
  font-weight: 600;
}

.faq-answer :deep(em) {
  color: #666;
  font-style: italic;
}

.faq-answer :deep(a) {
  color: #1976d2;
  text-decoration: none;
}

.faq-answer :deep(a:hover) {
  text-decoration: underline;
}

/* Custom scrollbar */
.faq-content::-webkit-scrollbar {
  width: 8px;
}

.faq-content::-webkit-scrollbar-track {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 4px;
}

.faq-content::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-primary), 0.5);
  border-radius: 4px;
}

.faq-content::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-primary), 0.7);
}

/* Mobile responsiveness */
@media (max-width: 960px) {
  .faq-content {
    max-height: 75vh;
  }
  
  .faq-answer {
    font-size: 0.9rem;
  }
}

@media (max-width: 600px) {
  .faq-view {
    padding: 12px 0;
  }
  
  .faq-content {
    max-height: 70vh;
  }
  
  .faq-answer {
    font-size: 0.85rem;
  }
}
</style>
