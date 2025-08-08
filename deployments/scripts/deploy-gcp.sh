#!/bin/bash

# NeMo Guardrails GCP Kubernetes Deployment Script
# Clean deployment script that consolidates Docker patterns for GCP/K8s
# Uses separate rail configuration files for easier editing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration - Use existing project
PROJECT_ID=$(gcloud config get-value project)
CLUSTER_NAME="nemo-guardrails-cluster"
REGION="us-west1"
NAMESPACE="nemo-guardrails"

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

# Parse command line arguments
DEPLOYMENT_TYPE="production"
SKIP_BUILD=false
SKIP_TESTS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --type=*)
            DEPLOYMENT_TYPE="${1#*=}"
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [--type=production|basic|maximum] [--skip-build] [--skip-tests]"
            echo "  --type: Deployment type (default: production)"
            echo "  --skip-build: Skip Docker image build"
            echo "  --skip-tests: Skip health checks and tests"
            exit 0
            ;;
        *)
            print_error "Unknown option $1"
            exit 1
            ;;
    esac
done

print_status "🚀 Starting NeMo Guardrails GCP Deployment (Type: $DEPLOYMENT_TYPE)"

# Check prerequisites
print_status "🔍 Checking prerequisites..."

# Check if gcloud is available
if ! command -v gcloud > /dev/null 2>&1; then
    print_error "gcloud CLI is not installed. Please install Google Cloud SDK."
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl > /dev/null 2>&1; then
    print_error "kubectl is not installed. Please install kubectl."
    exit 1
fi

# Check if Docker is running (only if not skipping build)
if [ "$SKIP_BUILD" = false ]; then
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker or use --skip-build."
        exit 1
    fi
fi

# Check authentication
print_status "🔐 Checking GCP authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q "@"; then
    print_error "No active GCP authentication. Please run: gcloud auth login"
    exit 1
fi

print_status "📋 Using GCP project: $PROJECT_ID"

# Get cluster credentials
print_status "🔑 Getting GKE cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Create namespace if it doesn't exist
print_status "📁 Creating namespace '$NAMESPACE'..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Build and push Docker image (unless skipping)
if [ "$SKIP_BUILD" = false ]; then
    print_status "🏗️  Building and pushing Docker image..."
    
    # Build the image
    docker build -t gcr.io/$PROJECT_ID/nemo-guardrails:latest -f Dockerfile.full .
    
    # Push to GCR
    docker push gcr.io/$PROJECT_ID/nemo-guardrails:latest
    
    print_success "✅ Docker image built and pushed"
else
    print_warning "⚠️  Skipping Docker build (--skip-build specified)"
fi

# Deploy based on type
print_status "🚀 Deploying $DEPLOYMENT_TYPE configuration..."

case $DEPLOYMENT_TYPE in
    "basic")
        DEPLOYMENT_FILE="k8s-deployments/basic-secure-deployment.yaml"
        CONFIG_TYPE="basic_security"
        RAILS_FILE="configs/basic_security_rails.co"
        ;;
    "maximum")
        DEPLOYMENT_FILE="k8s-deployments/maximum-secure-deployment.yaml"
        CONFIG_TYPE="maximum_security"
        RAILS_FILE="configs/maximum_security_rails.co"
        ;;
    "production"|*)
        DEPLOYMENT_FILE="k8s-deployments/production-secure-deployment.yaml"
        CONFIG_TYPE="production_security"
        RAILS_FILE="configs/production_security_rails.co"
        ;;
esac

# Check if deployment files exist
if [ ! -f "$DEPLOYMENT_FILE" ]; then
    print_error "Deployment file $DEPLOYMENT_FILE not found!"
    exit 1
fi

if [ ! -f "$RAILS_FILE" ]; then
    print_error "Rails configuration file $RAILS_FILE not found!"
    exit 1
fi

print_status "📋 Using deployment file: $DEPLOYMENT_FILE"
print_status "🛡️  Using rails config: $RAILS_FILE"

# Apply the deployment
kubectl apply -f $DEPLOYMENT_FILE -n $NAMESPACE

# Wait for deployment to be ready
print_status "⏳ Waiting for deployment to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/nemo-guardrails -n $NAMESPACE

# Wait additional time for services to initialize
print_status "⏳ Waiting for services to initialize..."
sleep 60

# Get service endpoints
print_status "🔍 Getting service endpoints..."
EXTERNAL_IP=$(kubectl get service nemo-guardrails-service -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")

if [ "$EXTERNAL_IP" = "pending" ] || [ -z "$EXTERNAL_IP" ]; then
    print_warning "⚠️  External IP is still pending, checking for NodePort..."
    NODE_PORT=$(kubectl get service nemo-guardrails-service -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "")
    if [ -n "$NODE_PORT" ]; then
        NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}' 2>/dev/null || echo "")
        if [ -n "$NODE_IP" ]; then
            ENDPOINT="http://$NODE_IP:$NODE_PORT"
        else
            ENDPOINT="http://localhost:8080"
            print_warning "⚠️  Using port-forward for testing: kubectl port-forward -n $NAMESPACE service/nemo-guardrails-service 8080:8000"
        fi
    else
        ENDPOINT="http://localhost:8080"
        print_warning "⚠️  Using port-forward for testing: kubectl port-forward -n $NAMESPACE service/nemo-guardrails-service 8080:8000"
    fi
else
    ENDPOINT="http://$EXTERNAL_IP"
fi

# Display deployment information
print_success "🌐 Deployment Information:"
echo "  • Deployment Type:     $DEPLOYMENT_TYPE"
echo "  • Configuration:       $CONFIG_TYPE"
echo "  • Rails File:          $RAILS_FILE"
echo "  • Namespace:           $NAMESPACE"
echo "  • Endpoint:            $ENDPOINT"
if [ "$EXTERNAL_IP" != "pending" ] && [ -n "$EXTERNAL_IP" ]; then
    echo "  • External IP:         $EXTERNAL_IP"
fi

# Run health checks and tests (unless skipping)
if [ "$SKIP_TESTS" = false ]; then
    print_status "🧪 Running health checks and tests..."
    
    # Wait a bit more for services to be fully ready
    sleep 30
    
    # Test health endpoint
    print_status "🔍 Testing health endpoint..."
    max_retries=10
    retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -f -s "$ENDPOINT/health" > /dev/null 2>&1; then
            print_success "✅ Health endpoint is responding"
            break
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -lt $max_retries ]; then
                print_status "⏳ Waiting for health endpoint (attempt $retry_count/$max_retries)..."
                sleep 10
            else
                print_error "❌ Health endpoint not responding after $max_retries attempts"
                print_status "🔧 Debug commands:"
                echo "  kubectl logs -n $NAMESPACE deployment/nemo-guardrails"
                echo "  kubectl describe pod -n $NAMESPACE -l app=nemo-guardrails"
                exit 1
            fi
        fi
    done
    
    # Test basic functionality
    print_status "🎯 Testing basic functionality..."
    response=$(curl -s -X POST "$ENDPOINT/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "config_id": "'$CONFIG_TYPE'"
        }' 2>/dev/null || echo "ERROR")
    
    if echo "$response" | grep -q "choices\|content" 2>/dev/null; then
        print_success "✅ Basic chat functionality is working"
    else
        print_warning "⚠️  Basic functionality test inconclusive"
    fi
    
    # Run security tests if test file exists
    if [ -f "dashboard_tests/test_production_security_deployment.py" ]; then
        print_status "🛡️  Running security tests..."
        cd dashboard_tests
        python -m pytest test_production_security_deployment.py -v --tb=short || print_warning "⚠️  Some security tests failed"
        cd ..
    fi
    
else
    print_warning "⚠️  Skipping tests (--skip-tests specified)"
fi

# Display useful commands
print_status "📋 Useful commands:"
echo "  • View logs:           kubectl logs -f -n $NAMESPACE deployment/nemo-guardrails"
echo "  • Check pods:          kubectl get pods -n $NAMESPACE"
echo "  • Check services:      kubectl get services -n $NAMESPACE"
echo "  • Port forward:        kubectl port-forward -n $NAMESPACE service/nemo-guardrails-service 8080:8000"
echo "  • Scale deployment:    kubectl scale deployment nemo-guardrails -n $NAMESPACE --replicas=3"
echo "  • Update deployment:   kubectl rollout restart deployment/nemo-guardrails -n $NAMESPACE"
echo "  • Delete deployment:   kubectl delete -f $DEPLOYMENT_FILE -n $NAMESPACE"

# Final status
print_success "🎉 GCP deployment complete!"
print_status "🔧 To edit security rules, modify: $RAILS_FILE"
print_status "🔄 To redeploy with changes: $0 --type=$DEPLOYMENT_TYPE"

if [ "$EXTERNAL_IP" = "pending" ] || [ -z "$EXTERNAL_IP" ]; then
    print_warning "💡 External IP is pending. Run 'kubectl get services -n $NAMESPACE' to check status."
fi

print_status "🌐 Your NeMo Guardrails endpoint: $ENDPOINT"