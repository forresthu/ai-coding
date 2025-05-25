# AI Models Dashboard - React Frontend

frontend: firebase
Project Console: https://console.firebase.google.com/project/a-test-6ef42/overview
Hosting URL: https://a-test-6ef42.web.app

Backend: Cloud run
https://ai-models-dashboard.uc.r.appspot.com

A modern React application that displays AI models with live data from Hugging Face Hub.

## Setup Instructions

1. **Install Node.js** (if not already installed)
   - Download from https://nodejs.org/
   - Choose LTS version

2. **Install dependencies**
   ```bash
   cd c:\projects\ai-coding\frontend
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```
   The app will open at http://localhost:3000

4. **Make sure the backend is running**
   - The backend should be running on http://localhost:5000
   - The React app is configured to proxy API requests to the backend

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm run eject` - Ejects from Create React App (not reversible)

## Features

- **Modern React Architecture**: Uses functional components with hooks
- **Component-Based Design**: Modular, reusable components
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: Graceful error states and retry functionality
- **Loading States**: Smooth loading indicators
- **Live Data**: Fetches real-time data from Hugging Face API
- **Company Branding**: Each model card styled with company colors

## Project Structure

```
src/
  ├── components/
  │   ├── ModelCard.js        # Individual model card component
  │   ├── LoadingSpinner.js   # Loading indicator component
  │   ├── ErrorMessage.js     # Error display component
  │   └── *.css              # Component-specific styles
  ├── App.js                 # Main application component
  ├── App.css               # Main application styles
  ├── index.js              # React entry point
  └── index.css             # Global styles
```

## Backend Integration

The frontend expects the backend API to be available at:
- Development: `http://localhost:5000/api`
- Production: Configure `API_BASE` in App.js

Required API endpoints:
- `GET /api/models` - Returns all models by category
- `GET /api/models/<category>` - Returns models for specific category
- `GET /api/model/<model_id>` - Returns details for specific model