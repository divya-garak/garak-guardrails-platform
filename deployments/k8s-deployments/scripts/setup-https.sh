#!/bin/bash
set -e

echo "🔧 Setting up HTTPS for api.garaksecurity.com"

# 1. Install NGINX Ingress Controller
echo "📦 Installing NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Wait for ingress controller
echo "⏳ Waiting for ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

# 2. Install cert-manager
echo "📦 Installing cert-manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for cert-manager
echo "⏳ Waiting for cert-manager to be ready..."
kubectl wait --namespace cert-manager \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/name=cert-manager \
  --timeout=300s

# 3. Apply SSL configuration
echo "🔒 Applying SSL configuration..."
kubectl apply -f ../k8s-manifests/ingress-ssl.yaml

# 4. Get ingress IP
echo "📡 Getting ingress external IP..."
kubectl get ingress nemo-guardrails-ingress

echo "✅ HTTPS setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Point api.garaksecurity.com DNS A record to the ingress IP above"
echo "2. Wait 5-10 minutes for Let's Encrypt certificate"
echo "3. Test: curl https://api.garaksecurity.com/"