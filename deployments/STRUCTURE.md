# K8s Deployment Structure

## ✅ Clean, Organized Deployment Directory

All deployment-related files have been moved from the repository root to this organized structure:

```
k8s-deployments/
├── 📖 README.md              # Comprehensive deployment guide
├── 🚀 deploy.sh              # Main deployment script with options
├── 📋 STRUCTURE.md           # This file - directory overview
│
├── 🐳 dockerfiles/           # Container build configurations
│   ├── Dockerfile            # Default container
│   ├── Dockerfile.full       # Production with all security features ⭐
│   └── Dockerfile.simple     # Basic deployment
│
├── ⚙️  scripts/              # Deployment automation
│   ├── deploy-https.sh       # HTTPS production deployment ⭐
│   ├── setup-https.sh        # HTTPS infrastructure setup
│   ├── deploy_gcp_production_security.sh  # Security-focused
│   ├── deploy-gcp.sh         # Basic GCP deployment
│   ├── deploy-light.sh       # Lightweight deployment
│   └── deploy.sh             # Legacy deployment script
│
└── 📄 k8s-manifests/         # Kubernetes resource definitions
    ├── ingress-ssl.yaml      # HTTPS ingress with Let's Encrypt ⭐
    ├── service-for-ingress.yaml  # ClusterIP service for ingress
    ├── simple-nemo-deployment.yaml  # Main application deployment ⭐
    ├── redis-deployment.yaml  # Redis cache for sessions
    ├── load-balancer.yaml    # External load balancer
    ├── monitoring-deployment.yaml  # Monitoring stack
    ├── nemo-deployment.yaml  # Alternative deployment config
    └── cloudbuild.yaml       # Google Cloud Build CI/CD
```

## 🎯 Quick Deployment

### Production HTTPS (Recommended)
```bash
cd k8s-deployments
./deploy.sh
# Select option 1 for HTTPS Production Deployment
```

### Manual Steps
```bash
cd k8s-deployments
./scripts/deploy-https.sh
```

## 🧹 Cleanup Completed

### Files Moved FROM Root:
- ❌ `deploy*.sh` → ✅ `scripts/`
- ❌ `setup-https.sh` → ✅ `scripts/`
- ❌ `Dockerfile*` → ✅ `dockerfiles/`
- ❌ `*.yaml` (deployment files) → ✅ `k8s-manifests/`

### Files Removed:
- 🗑️ Redundant `dockerfiles/` directory in root
- 🗑️ Duplicate deployment files

## 🚀 Current Production Status

**Live Deployment**: https://api.garaksecurity.com (pending DNS update)
**Infrastructure**: GKE with NGINX Ingress + Let's Encrypt SSL
**Security**: Full guardrails with jailbreak detection and content safety
**Monitoring**: Health checks and comprehensive logging enabled

---
⭐ = **Production Ready** | ✅ = **Organized** | 🎯 = **Recommended**