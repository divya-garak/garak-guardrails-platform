#!/bin/bash
set -e

echo "🚀 Deploying HTTPS for api.garaksecurity.com"

# 1. Create the ingress service
echo "📦 Creating ingress-compatible service..."
kubectl apply -f ../k8s-manifests/service-for-ingress.yaml

# 2. Run HTTPS setup
echo "🔒 Setting up HTTPS components..."
./setup-https.sh

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Manual steps required:"
echo "1. Add DNS A record: api.garaksecurity.com → [INGRESS_IP from above]"
echo "2. Wait 5-10 minutes for certificate provisioning"
echo "3. Test HTTPS endpoint:"
echo "   curl https://api.garaksecurity.com/"
echo "   curl https://api.garaksecurity.com/v1/chat/completions \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"config_id\":\"main\",\"messages\":[{\"role\":\"user\",\"content\":\"Hello!\"}]}'"