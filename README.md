# ATS-Friendly Resume Generator

A modern web application that generates ATS-optimized resumes tailored to specific job descriptions using AI. The application uses Groq's LLM API for intelligent resume generation and provides a user-friendly interface for both file uploads and text input.

## Project Architecture

### Frontend (Vue.js + Vuetify)
- Built with Vue 3 and TypeScript
- Uses Vuetify for Material Design components
- Features:
  - Dual input methods (file upload and text paste)
  - Real-time validation
  - Copy to clipboard functionality
  - Smart file naming for downloads
  - Responsive design

### Backend (FastAPI)
- Python-based REST API
- Uses Groq's LLM for AI-powered resume generation
- Features:
  - Job title extraction
  - ATS-optimized content generation
  - Environment-based configuration
  - Comprehensive error handling
  - File processing capabilities

## Prerequisites

- Node.js (v16 or higher)
- Python 3.10 or higher
- Groq API key (get it from [Groq Console](https://console.groq.com))

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit .env and add your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   GROQ_MODEL=mixtral-8x7b-32768
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn app.main:app --reload
   ```
   The backend will run on http://localhost:8000

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will run on http://localhost:3000

Alternatively, use the provided start script:
```bash
./start-servers.sh
```

## Usage

1. Access the application at http://localhost:3000

2. Choose your input method:
   - **File Upload**: Upload a job description file (.txt, .pdf, .doc, .docx)
   - **Text Input**: Paste the job description directly

3. Click "Generate Resume" to create an ATS-optimized resume

4. Use the provided options to:
   - Copy the resume to clipboard
   - Download the resume as a text file (automatically named based on the job title)

## Features

- **Dual Input Methods**: Support for both file uploads and text input
- **AI-Powered Generation**: Uses Groq's LLM for intelligent resume creation
- **ATS Optimization**: Ensures resumes are compatible with Applicant Tracking Systems
- **Smart Naming**: Automatically extracts job titles for organized file naming
- **Error Handling**: Comprehensive error handling and user feedback
- **Responsive Design**: Works on both desktop and mobile devices

## Project Structure

```
resume_builder/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ResumeBuilder.vue
│   │   ├── plugins/
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.ts
└── start-servers.sh
```

## API Endpoints

- `POST /api/generate-resume`: Generate a resume from a job description
- `GET /api/health`: Check API health and configuration

## Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Empty inputs
- API failures
- Rate limiting
- Network issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use this project for personal or commercial purposes.
