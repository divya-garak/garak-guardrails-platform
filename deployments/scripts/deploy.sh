#!/bin/bash
set -e

echo "🚀 NeMo Guardrails - Production Deployment with HTTPS"
echo "======================================================"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is required but not installed. Please install kubectl first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -d "k8s-manifests" ] || [ ! -d "scripts" ]; then
    echo "❌ Please run this script from the k8s-deployments directory"
    echo "   cd k8s-deployments && ./deploy.sh"
    exit 1
fi

echo "📋 Deployment Options:"
echo "1. HTTPS Production Deployment (Recommended)"
echo "2. Basic GCP Deployment"
echo "3. Security-focused Deployment"
echo "4. Lightweight Deployment"
echo ""

read -p "Select deployment type (1-4): " choice

case $choice in
    1)
        echo "🔒 Starting HTTPS Production Deployment..."
        cd scripts
        ./deploy-https.sh
        ;;
    2)
        echo "☁️  Starting Basic GCP Deployment..."
        cd scripts
        ./deploy-gcp.sh
        ;;
    3)
        echo "🛡️  Starting Security-focused Deployment..."
        cd scripts
        ./deploy_gcp_production_security.sh
        ;;
    4)
        echo "⚡ Starting Lightweight Deployment..."
        cd scripts
        ./deploy-light.sh
        ;;
    *)
        echo "❌ Invalid selection. Please choose 1-4."
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment script completed!"
echo ""
echo "📊 Check deployment status:"
echo "kubectl get pods"
echo "kubectl get ingress"
echo "kubectl get services"