#!/bin/bash
# Deployment script for Manus Backend

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if config file exists
if [ ! -f "config/config.yaml" ]; then
    echo "Config file not found. Creating from example..."
    mkdir -p config
    cp config/config.yaml.example config/config.yaml
    echo "Please edit config/config.yaml to add your API keys."
    exit 1
fi

# Check for API keys in environment
if [ -z "$OPENAI_API_KEY" ] || [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: API keys not found in environment variables."
    echo "Please set OPENAI_API_KEY and ANTHROPIC_API_KEY environment variables or add them to config/config.yaml."
fi

# Build and start the containers
echo "Building and starting Manus Backend..."
docker-compose up -d --build

# Check if the service is running
if [ $? -eq 0 ]; then
    echo "Manus Backend is now running at http://localhost:8000"
    echo "API documentation is available at http://localhost:8000/docs"
else
    echo "Failed to start Manus Backend. Please check the logs with 'docker-compose logs'."
    exit 1
fi
