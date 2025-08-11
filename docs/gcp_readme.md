# NeMo Guardrails GCP Cluster Status

## Current Deployment Overview

### Cluster Information
- **Cluster Name**: `nemo-guardrails-cluster`
- **Project**: `garak-shield`
- **Region**: `us-west1`
- **Status**: `RUNNING`
- **Master Version**: `1.33.2-gke.1240000`
- **Created**: August 1, 2025

### Node Pool Configuration

#### Default Pool (CPU Workloads)
- **Machine Type**: `e2-standard-4` (4 vCPU, 16GB RAM)
- **Current Nodes**: 6 nodes
- **Disk**: 100GB SSD persistent disk per node
- **Autoscaling**: 1-10 nodes
- **Purpose**: Core NeMo services, Presidio, content safety, jailbreak detection

#### GPU Pool (AI/ML Workloads)
- **Machine Type**: `n1-standard-4` + NVIDIA Tesla T4
- **Current Nodes**: 0 (scales on demand)
- **GPU**: 1x NVIDIA T4 per node
- **Disk**: 200GB SSD persistent disk per node
- **Autoscaling**: 0-3 nodes
- **Zones**: `us-west1-a`, `us-west1-b` (T4 availability)
- **Taints**: `nvidia.com/gpu=present:NoSchedule`
- **Purpose**: LlamaGuard, GPU-accelerated detection services

### Supporting Infrastructure

#### Storage Resources
- **Cloud Storage Bucket**: `gs://garak-shield-guardrails-models/`
  - Purpose: ML models, configurations, backups
  - Location: `us-west1`
  - Storage Class: `STANDARD`

#### Cache Layer
- **Redis Instance**: `guardrails-cache`
  - Version: `REDIS_6_X`
  - Tier: `STANDARD_HA` (High Availability)
  - Size: 1GB
  - Host: `10.125.160.180:6379`
  - Network: VPC default network
  - Status: `READY`

#### Security & Secrets
- **Kubernetes Secrets**: `api-keys`
  - OpenAI API key (placeholder)
  - NVIDIA API key (placeholder)
  - HuggingFace token (placeholder)
- **Google Secret Manager**: Centralized secret storage
  - `openai-api-key`
  - `nvidia-api-key`
  - `huggingface-token`

### GPU Support
- **NVIDIA Driver Installer**: Deployed as DaemonSet
- **GPU Device Plugins**: Installed for different GPU configurations
  - Small, Medium, Large profiles
  - COS and Ubuntu support
- **Driver Status**: Ready for GPU workload scheduling

### Network Configuration
- **Cluster Type**: Regional (multi-zone)
- **IP Alias**: Enabled (VPC-native)
- **Network Policy**: Enabled
- **Private Endpoint**: Available for secure access

### Monitoring & Logging
- **Cloud Logging**: Enabled (SYSTEM, WORKLOAD)
- **Cloud Monitoring**: Enabled (SYSTEM)
- **Auto-repair**: Enabled
- **Auto-upgrade**: Enabled

## Current Capabilities

### Ready for Deployment
✅ **Core NeMo Guardrails Services** - CPU nodes available  
✅ **LlamaGuard GPU Services** - GPU pool ready to scale  
✅ **Presidio PII Detection** - CPU nodes available  
✅ **Content Safety Services** - CPU nodes available  
✅ **Jailbreak Detection** - CPU/GPU nodes available  
✅ **Fact Checking Services** - CPU nodes available  

### Infrastructure Status
✅ **Container Registry**: Ready for image storage  
✅ **Load Balancing**: Ready for ingress configuration  
✅ **Secret Management**: API keys configured  
✅ **Storage**: Cloud Storage and Redis cache ready  
✅ **Auto-scaling**: HPA and cluster autoscaler ready  

## Cost Optimization Features

### Active Cost Controls
- **GPU Nodes**: Scale to zero when not in use
- **Preemptible Options**: Available for fault-tolerant workloads
- **Auto-scaling**: Nodes scale down during low usage
- **Regional Persistent Disks**: Cross-zone redundancy without snapshots

### Current Resource Usage
- **CPU Nodes**: 6/10 max (can scale down to 1)
- **GPU Nodes**: 0/3 max (scales up on workload demand)
- **Storage**: Minimal usage in Cloud Storage bucket
- **Redis**: 1GB standard instance

## Next Steps

### Phase 1: Container Images
1. Build and push NeMo Guardrails images to `gcr.io/garak-shield/`
2. Build specialized service images (LlamaGuard, Presidio, etc.)
3. Configure image security scanning

### Phase 2: Service Deployment
1. Deploy core NeMo Guardrails service
2. Deploy LlamaGuard GPU service
3. Deploy supporting detection services
4. Configure service mesh and networking

### Phase 3: Production Setup
1. Configure load balancer and ingress
2. Setup SSL certificates and domain
3. Deploy monitoring and alerting
4. Configure auto-scaling policies

## Access Information

### Cluster Access
```bash
# Set environment variables
export PROJECT_ID="garak-shield"
export REGION="us-west1"
export CLUSTER_NAME="nemo-guardrails-cluster"

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION

# Verify access
kubectl get nodes
```

### Required Environment Setup
```bash
# Add GKE auth plugin to PATH
export PATH="$PATH:/opt/homebrew/share/google-cloud-sdk/bin"
export USE_GKE_GCLOUD_AUTH_PLUGIN=True
```

## Resource Endpoints

- **Cluster**: `https://35.247.51.161` (Master IP)
- **Redis Cache**: `10.125.160.180:6379`
- **Storage**: `gs://garak-shield-guardrails-models/`
- **Container Registry**: `gcr.io/garak-shield/`

---

*Last Updated: August 1, 2025*  
*Status: Infrastructure Ready - Deployment Phase*