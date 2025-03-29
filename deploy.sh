#!/bin/bash
# Script to deploy and run the Manus Platform Backend

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

# Check if .env file exists
if [ ! -f .env ]; then
    echo "No .env file found. Creating from example..."
    cp .env.example .env
    echo "Please edit .env file with your API keys before continuing."
    exit 1
fi

# Build and start the containers
echo "Building and starting containers..."
docker-compose up -d --build

# Wait for the API to start
echo "Waiting for API to start..."
sleep 5

# Run the tests
echo "Running tests..."
docker-compose exec api python -m tests.test_api

echo "Deployment complete! API is running at http://localhost:8000"
echo "You can check the API documentation at http://localhost:8000/docs"
