#!/bin/bash

echo "🚀 Deploying BD-King-R7 AI Website..."

# Pull latest changes
git pull origin main

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start new containers
echo "🐳 Building and starting new containers..."
docker-compose up --build -d

# Run database migrations (if any)
echo "🗃️ Running database migrations..."
docker-compose exec backend node scripts/migrate.js

echo "✅ Deployment complete!"
echo "🌐 Your updated BD-King-R7 website is now live!"