#!/bin/bash

echo "🚀 Deploying AI Models Dashboard to GCP..."

# Deploy Backend
echo "📡 Deploying Backend to App Engine..."
cd backend
gcloud app deploy --quiet
cd ..

# Build and Deploy Frontend
echo "🌐 Building and Deploying Frontend to Firebase..."
cd frontend
npm run build
firebase deploy --only hosting
cd ..

echo "✅ Deployment Complete!"
echo "🌐 Frontend: https://ai-models-dashboard.web.app"
echo "📡 Backend: https://ai-models-dashboard.uc.r.appspot.com"