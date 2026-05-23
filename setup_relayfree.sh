#!/bin/bash

# Setup script for RelayFreeLLM

echo "🚀 Setting up RelayFreeLLM for free AI code reviews..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if RelayFreeLLM is already running
if docker ps | grep -q relayfree_llm; then
    echo "✅ RelayFreeLLM is already running on http://localhost:8000"
else
    echo "📦 Starting RelayFreeLLM container..."
    docker-compose up -d
    
    # Wait for health check
    echo "⏳ Waiting for RelayFreeLLM to be ready..."
    sleep 10
    
    # Check if it's working
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ RelayFreeLLM is now running on http://localhost:8000"
    else
        echo "⚠️  RelayFreeLLM may still be starting. Check with: docker logs relayfree_llm"
    fi
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete! You can now run: python src/main.py"
echo ""
echo "📝 Note: If RelayFreeLLM isn't working, check:"
echo "   - Docker logs relayfree_llm"
echo "   - Make sure port 8000 is not in use"
echo "   - Add API keys to .env file for better rate limits"