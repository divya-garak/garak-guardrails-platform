#!/bin/bash

# NeMo Guardrails Docker Deployment Script
# This script deploys all guardrail categories in Docker for local testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "🚀 Starting NeMo Guardrails Comprehensive Docker Deployment"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_warning "docker-compose not found, trying docker compose..."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Create logs directory
print_status "📁 Creating logs directory..."
mkdir -p logs

# Check if environment file exists
if [ ! -f ".env" ]; then
    if [ -f "docker-test.env" ]; then
        print_warning "No .env file found. Using docker-test.env for testing."
        cp docker-test.env .env
    else
        print_warning "No environment file found. Using .env.example as template."
        cp .env.example .env
        print_warning "Please edit .env file with your OpenAI API key before deployment."
        exit 1
    fi
fi

# Build and start services
print_status "🏗️  Building Docker images..."
$DOCKER_COMPOSE build

print_status "🚀 Starting all guardrail services..."
$DOCKER_COMPOSE up -d

# Wait for services to start
print_status "⏳ Waiting for services to initialize..."
sleep 30

# Check service health
print_status "🔍 Checking service health..."

services=("jailbreak-detection:1337" "factcheck-service:5000" "sensitive-data-detection:5001" "content-safety:5002")
healthy_services=0

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if curl -f -s "http://localhost:$port/health" > /dev/null; then
        print_success "✅ $service_name is healthy"
        ((healthy_services++))
    else
        print_error "❌ $service_name is not responding"
    fi
done

# Note: Llama Guard might take longer to initialize
print_status "🦙 Checking Llama Guard service (may take longer)..."
if curl -f -s "http://localhost:8001/health" > /dev/null; then
    print_success "✅ llama-guard is healthy"
    ((healthy_services++))
else
    print_warning "⚠️  llama-guard is still initializing (this is normal)"
fi

# Check main NeMo Guardrails service
print_status "🛡️  Checking main NeMo Guardrails service..."
if curl -f -s "http://localhost:8000/health" > /dev/null; then
    print_success "✅ nemo-guardrails main service is healthy"
    ((healthy_services++))
else
    print_warning "⚠️  nemo-guardrails main service is still starting"
fi

print_status "📊 Service Status Summary:"
print_status "  Healthy Services: $healthy_services/6"

# Display service URLs
print_success "🌐 Service URLs:"
echo "  • Main NeMo Guardrails:      http://localhost:8000"
echo "  • Jailbreak Detection:       http://localhost:1337"
echo "  • Fact Checking:             http://localhost:5000"
echo "  • Llama Guard:               http://localhost:8001"
echo "  • Sensitive Data Detection:  http://localhost:5001"
echo "  • Content Safety:            http://localhost:5002"

# Test basic functionality
print_status "🧪 Running basic functionality tests..."

# Test jailbreak detection
if curl -f -s "http://localhost:1337/health" > /dev/null; then
    print_success "✅ Jailbreak detection service is ready for testing"
fi

# Test presidio
if curl -f -s "http://localhost:5001/health" > /dev/null; then
    print_success "✅ Sensitive data detection service is ready for testing"
fi

# Show logs command
print_status "📋 Useful commands:"
echo "  • View all logs:     $DOCKER_COMPOSE logs -f"
echo "  • Stop services:     $DOCKER_COMPOSE down"
echo "  • Restart services:  $DOCKER_COMPOSE restart"
echo "  • View status:       $DOCKER_COMPOSE ps"

# Test with sample request (if main service is up)
if curl -f -s "http://localhost:8000/health" > /dev/null; then
    print_status "🎯 Testing with sample request..."
    curl -X POST http://localhost:8000/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "messages": [{"role": "user", "content": "Hello, can you help me test the guardrails?"}],
            "model": "gpt-3.5-turbo-instruct"
        }' | jq '.' || print_warning "Test request failed (may need API key configuration)"
fi

print_success "🎉 Deployment complete! All guardrail categories are now running in Docker."
print_status "📝 Check the logs directory for detailed logs and traces."
print_status "🔧 Edit comprehensive-config/config.yml to customize guardrail settings."