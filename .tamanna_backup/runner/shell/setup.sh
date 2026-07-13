#!/bin/bash

echo "🚀 Setting up BD-King-R7 AI Website..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p nginx/ssl
mkdir -p database

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up --build -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are healthy
echo "🔍 Checking service health..."
curl -f http://localhost/health || echo "❌ Backend health check failed"
curl -f http://localhost/ai-health || echo "❌ AI service health check failed"

echo "✅ Setup complete!"
echo "🌐 Frontend: https://www.bd-king-r7.com"
echo "🔧 Backend API: https://www.bd-king-r7.com/api"
echo "🤖 AI Service: https://www.bd-king-r7.com/ai-health"