#!/bin/bash

# Real Estate Agent Marketing System - Startup Script

echo "🏠 Real Estate Agent Marketing System"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your API keys before proceeding."
    echo "   Required keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - JWT_SECRET (generate a random string)"
    echo "   - NEXTAUTH_SECRET (generate a random string)"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

echo "🚀 Starting Real Estate Agent Marketing System..."
echo ""

# Start the services
echo "📦 Building and starting Docker containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "🎉 System is starting up!"
echo ""
echo "📍 Access URLs:"
echo "   Frontend Dashboard:  http://localhost:3000"
echo "   API Documentation:   http://localhost:8000/docs"
echo "   AG2 Core Status:     http://localhost:8001/health"
echo "   Langflow UI:         http://localhost:7860"
echo "   Monitoring:          http://localhost:3001 (admin/admin)"
echo ""
echo "📊 Monitoring Commands:"
echo "   View logs:           docker-compose logs -f"
echo "   Stop system:         docker-compose down"
echo "   Restart:             docker-compose restart"
echo ""
echo "✨ Happy real estate marketing! 🏠"
