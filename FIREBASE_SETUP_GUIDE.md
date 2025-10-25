# 🚀 SpeechCoach AI - Firebase Integration Setup Guide

## 📋 Overview

This guide will help you set up SpeechCoach AI with Firebase authentication integration, featuring a modern Next.js frontend with Tailwind CSS and a FastAPI backend with Firebase Admin SDK.

## 🏗️ Architecture

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, Firebase Auth
- **Backend**: FastAPI with Firebase Admin SDK, Firestore integration
- **Authentication**: Firebase Authentication with JWT tokens
- **Database**: Firestore for user data and session storage
- **AI Services**: SYSTRAN Whisper + Google ADK for speech analysis

## 🔧 Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- Firebase project with Authentication and Firestore enabled
- Google Cloud Console access

## 📦 Installation Steps

### 1. Firebase Project Setup

1. **Create Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Create a new project
   - Enable Authentication (Email/Password and Google)
   - Enable Firestore Database

2. **Get Firebase Configuration**:
   - Go to Project Settings > General
   - Copy the Firebase config object
   - Download the service account key (JSON file)

3. **Configure Authentication**:
   - Go to Authentication > Sign-in method
   - Enable Email/Password
   - Enable Google sign-in
   - Add your domain to authorized domains

### 2. Backend Setup

```bash
# Navigate to project root
cd "/Users/yug/Desktop/HACKATHON2 copy"

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your Firebase credentials
```

**Environment Variables**:
```env
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id
GOOGLE_API_KEY=your-google-api-key
```

### 3. Frontend Setup

```bash
# Navigate to Next.js project
cd frontend/speechcoach-nextjs

# Install dependencies
npm install

# Set up environment variables
cp env.example .env.local
# Edit .env.local with your Firebase config
```

**Environment Variables**:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-firebase-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_API_URL=http://localhost:8002
```

## 🚀 Running the Application

### Start Backend Server
```bash
cd "/Users/yug/Desktop/HACKATHON2 copy"
python main.py
```
Backend will run on `http://localhost:8002`

### Start Frontend Server
```bash
cd frontend/speechcoach-nextjs
npm run dev
```
Frontend will run on `http://localhost:3000`

## 🔐 Authentication Flow

### Frontend (Next.js)
1. **Firebase Auth Context**: Manages authentication state
2. **Auth Components**: Modern sign-in/sign-up forms with Tailwind CSS
3. **Protected Routes**: Redirects unauthenticated users
4. **JWT Tokens**: Automatically included in API requests

### Backend (FastAPI)
1. **Firebase Admin SDK**: Verifies JWT tokens
2. **User Management**: Creates/updates user documents in Firestore
3. **Session Storage**: Saves speech analysis sessions
4. **Protected Endpoints**: Requires valid authentication

## 📊 Database Schema

### Firestore Collections

**Users Collection** (`/users/{uid}`):
```json
{
  "uid": "string",
  "email": "string",
  "display_name": "string",
  "created_at": "timestamp",
  "last_login_at": "timestamp",
  "total_sessions": "number",
  "average_clarity_score": "number",
  "total_filler_words": "number"
}
```

**Sessions Subcollection** (`/users/{uid}/sessions/{sessionId}`):
```json
{
  "type": "audio_analysis" | "text_analysis",
  "transcription": {
    "text": "string",
    "language": "string",
    "duration": "number",
    "confidence": "number"
  },
  "analysis": {
    "filler_count": "number",
    "clarity_score": "number",
    "suggestions": ["string"],
    "summary": "string",
    "filler_density": "number",
    "total_words": "number"
  },
  "metadata": {
    "filename": "string",
    "file_size": "number",
    "user_id": "string",
    "timestamp": "timestamp"
  },
  "created_at": "timestamp"
}
```

## 🎨 Frontend Features

### Modern UI Components
- **Authentication Modal**: Beautiful sign-in/sign-up forms
- **User Menu**: Profile management and logout
- **Analysis Dashboard**: Speech analysis with charts
- **Progress Tracking**: Historical session data
- **Responsive Design**: Mobile-first approach

### Key Pages
- `/` - Landing page with hero section
- `/auth` - Authentication page
- `/analysis` - Speech analysis interface
- `/dashboard` - User dashboard (protected)
- `/history` - Session history (protected)

## 🔌 API Endpoints

### Authentication Required
- `POST /analyze-speech` - Analyze audio file
- `POST /analyze-text` - Analyze text transcript
- `GET /user/profile` - Get user profile
- `GET /user/sessions` - Get user sessions
- `GET /user/stats` - Get user statistics
- `POST /user/save-session` - Save analysis session

### Public Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health check

## 🛡️ Security Features

- **JWT Token Verification**: Firebase Admin SDK validation
- **CORS Configuration**: Secure cross-origin requests
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error responses
- **Rate Limiting**: Built-in FastAPI rate limiting

## 🎯 Key Features

### Authentication
- ✅ Email/Password authentication
- ✅ Google OAuth integration
- ✅ Password reset functionality
- ✅ User profile management
- ✅ Session persistence

### Speech Analysis
- ✅ Audio file upload
- ✅ Live recording
- ✅ Text analysis
- ✅ Real-time feedback
- ✅ Progress tracking

### User Experience
- ✅ Modern, responsive design
- ✅ Smooth animations
- ✅ Interactive charts
- ✅ Mobile-friendly
- ✅ Accessibility features

## 🐛 Troubleshooting

### Common Issues

1. **Firebase Authentication Errors**:
   - Check Firebase project configuration
   - Verify API keys in environment variables
   - Ensure authorized domains are set

2. **CORS Issues**:
   - Update CORS origins in FastAPI configuration
   - Check frontend API URL configuration

3. **Firestore Permission Errors**:
   - Verify Firestore security rules
   - Check service account permissions

4. **Audio Analysis Failures**:
   - Ensure Google API key is valid
   - Check audio file format support
   - Verify microphone permissions

### Debug Mode
```bash
# Backend debug
DEBUG=true python main.py

# Frontend debug
NODE_ENV=development npm run dev
```

## 📈 Performance Optimization

- **Frontend**: Code splitting, lazy loading, image optimization
- **Backend**: Async operations, connection pooling
- **Database**: Indexed queries, efficient data structure
- **Caching**: Firebase caching, API response caching

## 🚀 Deployment

### Backend Deployment
- **Google Cloud Run**: Serverless container deployment
- **Railway**: Simple Python deployment
- **Heroku**: Traditional PaaS deployment

### Frontend Deployment
- **Vercel**: Optimized Next.js deployment
- **Netlify**: Static site deployment
- **Firebase Hosting**: Integrated Firebase deployment

## 📚 Additional Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy coding! 🎉**

For support or questions, please open an issue in the repository.

