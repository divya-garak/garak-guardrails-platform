#!/bin/bash
# deploy-static-ip.sh - Deploy static IP configuration for Garak Security

set -e

echo "🚀 Deploying Garak Security static IP configuration..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not authenticated with gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ kubectl not configured. Please configure kubectl for your GKE cluster${NC}"
    exit 1
fi

# Step 1: Create static IP (if not exists)
echo -e "${YELLOW}📡 Creating static IP...${NC}"
if gcloud compute addresses describe garak-guardrails-ip --global &> /dev/null; then
    echo -e "${GREEN}✅ Static IP 'garak-guardrails-ip' already exists${NC}"
    STATIC_IP=$(gcloud compute addresses describe garak-guardrails-ip --global --format="value(address)")
    echo -e "${GREEN}   IP Address: $STATIC_IP${NC}"
else
    echo "Creating new static IP..."
    gcloud compute addresses create garak-guardrails-ip \
      --global \
      --description="Static IP for Garak Security guardrails API endpoints"
    
    STATIC_IP=$(gcloud compute addresses describe garak-guardrails-ip --global --format="value(address)")
    echo -e "${GREEN}✅ Created static IP: $STATIC_IP${NC}"
fi

# Step 2: Apply Kubernetes configuration
echo -e "${YELLOW}🔧 Applying Kubernetes configuration...${NC}"
kubectl apply -f k8s-static-ip-setup.yaml

# Step 3: Wait for SSL certificate provisioning
echo -e "${YELLOW}🔒 Waiting for SSL certificate provisioning...${NC}"
echo "This may take 10-15 minutes for the certificate to be issued..."

# Check certificate status
for i in {1..30}; do
    STATUS=$(kubectl get managedcertificate garaksecurity-ssl-cert -o jsonpath='{.status.certificateStatus}' 2>/dev/null || echo "Provisioning")
    if [ "$STATUS" = "Active" ]; then
        echo -e "${GREEN}✅ SSL certificate is active!${NC}"
        break
    else
        echo "Certificate status: $STATUS (attempt $i/30)"
        sleep 30
    fi
done

# Step 4: Get ingress IP
echo -e "${YELLOW}🌐 Checking ingress status...${NC}"
sleep 10  # Wait a bit for ingress to initialize

INGRESS_IP=$(kubectl get ingress garaksecurity-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "Pending")
if [ "$INGRESS_IP" != "Pending" ] && [ "$INGRESS_IP" != "" ]; then
    echo -e "${GREEN}✅ Ingress IP: $INGRESS_IP${NC}"
    
    if [ "$INGRESS_IP" = "$STATIC_IP" ]; then
        echo -e "${GREEN}✅ Ingress is using the correct static IP!${NC}"
    else
        echo -e "${YELLOW}⚠️  Ingress IP ($INGRESS_IP) doesn't match static IP ($STATIC_IP)${NC}"
        echo "This may be normal during initial setup. Check again in 5-10 minutes."
    fi
else
    echo -e "${YELLOW}⏳ Ingress IP still pending. This is normal for new deployments.${NC}"
fi

# Step 5: DNS Configuration Instructions
echo -e "${YELLOW}📋 DNS Configuration Required:${NC}"
echo "Add these A records to your garaksecurity.com DNS in GoDaddy:"
echo ""
echo "Record Type: A"
echo "Name        : api"
echo "Value       : $STATIC_IP"
echo "TTL         : 1 Hour"
echo ""
echo "Record Type: A" 
echo "Name        : guardrails"
echo "Value       : $STATIC_IP"
echo "TTL         : 1 Hour"
echo ""
echo "Record Type: A"
echo "Name        : dashboard" 
echo "Value       : $STATIC_IP"
echo "TTL         : 1 Hour"
echo ""
echo "Record Type: A"
echo "Name        : docs"
echo "Value       : $STATIC_IP" 
echo "TTL         : 1 Hour"
echo ""

# Step 6: Testing instructions
echo -e "${YELLOW}🧪 Testing Instructions:${NC}"
echo "After DNS propagation (1-24 hours), test these endpoints:"
echo "• https://api.garaksecurity.com/"
echo "• https://guardrails.garaksecurity.com/"
echo "• https://dashboard.garaksecurity.com/"
echo "• https://docs.garaksecurity.com/docs"
echo ""
echo "Test DNS propagation with:"
echo "nslookup api.garaksecurity.com"
echo ""
echo "Test endpoints with:"
echo "curl -I https://api.garaksecurity.com/"

echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add DNS A records in GoDaddy (see above)"
echo "2. Wait for DNS propagation (1-24 hours)"
echo "3. Test HTTPS endpoints"
echo "4. Update your test suite to use new URLs"