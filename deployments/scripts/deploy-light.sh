#!/bin/bash

# NeMo Guardrails Light Docker Deployment Script
# This script deploys essential guardrails quickly for testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_status "🚀 Starting NeMo Guardrails Light Docker Deployment"

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
        print_warning "No environment file found. Please set OPENAI_API_KEY."
        echo "OPENAI_API_KEY=your_key_here" > .env
    fi
fi

# Build and start services using light configuration
print_status "🏗️  Building Docker images (light version)..."
$DOCKER_COMPOSE -f docker-compose.light.yml build

print_status "🚀 Starting essential guardrail services..."
$DOCKER_COMPOSE -f docker-compose.light.yml up -d

# Wait for services to start
print_status "⏳ Waiting for services to initialize..."
sleep 20

# Check service health
print_status "🔍 Checking service health..."

services=("jailbreak-detection:1337" "sensitive-data-detection:5001" "content-safety:5002")
healthy_services=0

for service in "${services[@]}"; do
    service_name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if curl -f -s "http://localhost:$port/health" > /dev/null; then
        print_success "✅ $service_name is healthy"
        ((healthy_services++))
    else
        print_warning "⚠️  $service_name is still starting"
    fi
done

# Check main NeMo Guardrails service
print_status "🛡️  Checking main NeMo Guardrails service..."
if curl -f -s "http://localhost:8000/health" > /dev/null; then
    print_success "✅ nemo-guardrails main service is healthy"
    ((healthy_services++))
else
    print_warning "⚠️  nemo-guardrails main service is still starting"
fi

print_status "📊 Service Status Summary:"
print_status "  Healthy Services: $healthy_services/4 (light version)"

# Display service URLs
print_success "🌐 Service URLs:"
echo "  • Main NeMo Guardrails:      http://localhost:8000"
echo "  • Jailbreak Detection:       http://localhost:1337"
echo "  • Sensitive Data Detection:  http://localhost:5001"
echo "  • Content Safety:            http://localhost:5002"

print_status "📋 Available commands:"
echo "  • View logs:         $DOCKER_COMPOSE -f docker-compose.light.yml logs -f"
echo "  • Stop services:     $DOCKER_COMPOSE -f docker-compose.light.yml down"
echo "  • Restart services:  $DOCKER_COMPOSE -f docker-compose.light.yml restart"
echo "  • Run tests:         python3 test_guardrails.py"

print_success "🎉 Light deployment complete!"
print_status "💡 For the full deployment with all services, use ./deploy.sh (requires more time and resources)"
print_status "🧪 Test the deployment with: python3 test_guardrails.py"