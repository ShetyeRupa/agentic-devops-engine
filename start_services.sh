#!/bin/bash

# Script to start all services for the agentic-devops-engine

echo "Starting services for agentic-devops-engine..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "Ollama is not installed. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Pull the model if not already present
if ! ollama list | grep -q "qwen2.5-coder:1.5b"; then
    echo "Pulling qwen2.5-coder:1.5b model..."
    ollama pull qwen2.5-coder:1.5b
fi

# Start LiteLLM proxy in background
echo "Starting LiteLLM proxy on port 8000..."
litellm --model ollama_chat/qwen2.5-coder:1.5b --port 8000 &

echo "Services started successfully."
echo ""
echo "To run your pipeline:"
echo "  source agentic_devops_engine/bin/activate"
echo "  python src/main.py"
echo ""
echo "To stop LiteLLM, run: pkill -f litellm"