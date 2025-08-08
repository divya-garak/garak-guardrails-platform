#!/bin/bash

# NeMo Guardrails Monitoring Deployment Script
# Deploys guardrails with comprehensive monitoring and control UI

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

print_status "🛡️ Starting NeMo Guardrails with Monitoring Dashboard"

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

# Stop any existing deployment
print_status "🛑 Stopping any existing deployments..."
$DOCKER_COMPOSE -f docker-compose.light.yml down 2>/dev/null || true
$DOCKER_COMPOSE -f docker-compose.monitoring.yml down 2>/dev/null || true

# Build and start services with monitoring
print_status "🏗️  Building Docker images with monitoring..."
$DOCKER_COMPOSE -f docker-compose.monitoring.yml build

print_status "🚀 Starting all services with monitoring..."
$DOCKER_COMPOSE -f docker-compose.monitoring.yml up -d

# Wait for services to start
print_status "⏳ Waiting for services to initialize..."
sleep 30

# Check service health
print_status "🔍 Checking service health..."

services=("jailbreak-detection:1337" "sensitive-data-detection:5001" "content-safety:5002" "guardrails-control-api:8080")
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
if curl -f -s "http://localhost:8000/" > /dev/null; then
    print_success "✅ nemo-guardrails main service is running"
    ((healthy_services++))
else
    print_warning "⚠️  nemo-guardrails main service is still starting"
fi

# Check monitoring dashboard
print_status "📊 Checking monitoring dashboard..."
if curl -f -s "http://localhost:8501/_stcore/health" > /dev/null; then
    print_success "✅ monitoring dashboard is healthy"
    ((healthy_services++))
else
    print_warning "⚠️  monitoring dashboard is still starting"
fi

print_status "📊 Service Status Summary:"
print_status "  Healthy Services: $healthy_services/6 (monitoring version)"

# Display service URLs
print_success "🌐 Service URLs:"
echo "  • 🛡️  Main NeMo Guardrails:       http://localhost:8000"
echo "  • 🔍 Jailbreak Detection:        http://localhost:1337"
echo "  • 🔒 Sensitive Data Detection:   http://localhost:5001"
echo "  • ⚡ Content Safety:             http://localhost:5002"
echo "  • 🎛️  Control API:               http://localhost:8080"
echo "  • 📊 Monitoring Dashboard:       http://localhost:8501"

print_status "📋 Available commands:"
echo "  • View logs:         $DOCKER_COMPOSE -f docker-compose.monitoring.yml logs -f"
echo "  • Stop services:     $DOCKER_COMPOSE -f docker-compose.monitoring.yml down"
echo "  • Restart services:  $DOCKER_COMPOSE -f docker-compose.monitoring.yml restart"
echo "  • API docs:          http://localhost:8080/docs"

# Test Control API
print_status "🧪 Testing Control API..."
sleep 5
if curl -f -s "http://localhost:8080/guardrails" > /dev/null; then
    print_success "✅ Control API is responding"
else
    print_warning "⚠️  Control API may still be starting"
fi

print_success "🎉 Monitoring deployment complete!"
print_status ""
print_status "🎯 Next Steps:"
echo "  1. Open monitoring dashboard: http://localhost:8501"
echo "  2. Use Control API: http://localhost:8080/docs"
echo "  3. Toggle guardrails in real-time"
echo "  4. Monitor service health and metrics"
echo ""
print_status "💡 Dashboard Features:"
echo "  • Real-time service health monitoring"
echo "  • Toggle individual guardrails on/off"
echo "  • Test guardrails with custom inputs"
echo "  • View and edit configuration"
echo "  • Track request metrics and response times"