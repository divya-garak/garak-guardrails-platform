# NeMo Guardrails GCP Deployment Guide
## Using gcloud CLI + kubectl

This guide provides step-by-step instructions to deploy all NeMo Guardrails services on Google Cloud Platform using only gcloud CLI and kubectl commands.

## Prerequisites

### 1. Install Required Tools
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install kubectl
gcloud components install kubectl

# Install Docker (for building images)
# Follow instructions for your OS at: https://docs.docker.com/get-docker/
```

### 2. Setup GCP Project
```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
export PROJECT_ID="nemo-guardrails-$(date +%s)"
gcloud projects create $PROJECT_ID

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    container.googleapis.com \
    cloudbuild.googleapis.com \
    storage-api.googleapis.com \
    redis.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com
```

### 3. Set Environment Variables
```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export ZONE="us-central1-a"
export CLUSTER_NAME="nemo-guardrails-cluster"
```

## Phase 1: Infrastructure Setup

### Step 1: Create GKE Cluster
```bash
# Create a GKE cluster with autoscaling
gcloud container clusters create $CLUSTER_NAME \
    --region=$REGION \
    --machine-type=e2-standard-4 \
    --num-nodes=2 \
    --enable-autoscaling \
    --min-nodes=1 \
    --max-nodes=10 \
    --enable-autorepair \
    --enable-autoupgrade \
    --enable-ip-alias \
    --enable-network-policy \
    --enable-cloud-logging \
    --enable-cloud-monitoring \
    --disk-size=100GB \
    --disk-type=pd-ssd

# Get cluster credentials
gcloud container clusters get-credentials $CLUSTER_NAME --region=$REGION
```

### Step 2: Create GPU Node Pool (for LlamaGuard)
```bash
# Create GPU node pool
gcloud container node-pools create gpu-pool \
    --cluster=$CLUSTER_NAME \
    --region=$REGION \
    --machine-type=n1-standard-4 \
    --accelerator=type=nvidia-tesla-t4,count=1 \
    --num-nodes=0 \
    --enable-autoscaling \
    --min-nodes=0 \
    --max-nodes=3 \
    --disk-size=200GB \
    --disk-type=pd-ssd \
    --node-taints=nvidia.com/gpu=present:NoSchedule

# Install NVIDIA GPU drivers
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/container-engine-accelerators/master/nvidia-driver-installer/cos/daemonset-preloaded.yaml
```

### Step 3: Create Storage Resources
```bash
# Create Cloud Storage bucket for models
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-guardrails-models

# Create Redis instance for caching
gcloud redis instances create guardrails-cache \
    --size=1 \
    --region=$REGION \
    --redis-version=redis_6_x \
    --tier=standard
```

### Step 4: Setup Secret Management
```bash
# Create secrets for API keys (replace with your actual keys)
gcloud secrets create openai-api-key --data-file=- <<< "your-openai-key-here"
gcloud secrets create nvidia-api-key --data-file=- <<< "your-nvidia-key-here"
gcloud secrets create huggingface-token --data-file=- <<< "your-hf-token-here"

# Create Kubernetes secrets
kubectl create secret generic api-keys \
    --from-literal=openai-key="your-openai-key-here" \
    --from-literal=nvidia-key="your-nvidia-key-here" \
    --from-literal=hf-token="your-hf-token-here"
```

## Phase 2: Build and Push Container Images

### Step 1: Setup Container Registry
```bash
# Configure Docker to use gcloud as credential helper
gcloud auth configure-docker

# Set image registry
export REGISTRY="gcr.io/$PROJECT_ID"
```

### Step 2: Build Core NeMo Image
```bash
# Build main NeMo Guardrails image
docker build -t $REGISTRY/nemo-guardrails:latest .
docker push $REGISTRY/nemo-guardrails:latest
```

### Step 3: Build Specialized Service Images
```bash
# Build LlamaGuard image
docker build -f Dockerfile.llamaguard -t $REGISTRY/llamaguard:latest .
docker push $REGISTRY/llamaguard:latest

# Build Content Safety image
docker build -f Dockerfile.content_safety -t $REGISTRY/content-safety:latest .
docker push $REGISTRY/content-safety:latest

# Build Presidio image
docker build -f Dockerfile.presidio -t $REGISTRY/presidio:latest .
docker push $REGISTRY/presidio:latest

# Build Jailbreak Detection image
docker build -f nemoguardrails/library/jailbreak_detection/Dockerfile \
    -t $REGISTRY/jailbreak-detection:latest .
docker push $REGISTRY/jailbreak-detection:latest

# Build Fact Checking image
docker build -f nemoguardrails/library/factchecking/align_score/Dockerfile \
    -t $REGISTRY/factcheck:latest .
docker push $REGISTRY/factcheck:latest
```

## Phase 3: Deploy Services

### Step 1: Create Namespace and RBAC
```bash
# Create namespace
kubectl create namespace nemo-guardrails

# Set default namespace
kubectl config set-context --current --namespace=nemo-guardrails
```

### Step 2: Deploy Core NeMo Guardrails Service
```bash
# Create deployment file
cat <<EOF > nemo-main-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemo-main
  namespace: nemo-guardrails
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nemo-main
  template:
    metadata:
      labels:
        app: nemo-main
    spec:
      containers:
      - name: nemo-main
        image: $REGISTRY/nemo-guardrails:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: nemo-main-service
  namespace: nemo-guardrails
spec:
  selector:
    app: nemo-main
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
EOF

# Apply the deployment
kubectl apply -f nemo-main-deployment.yaml
```

### Step 3: Deploy LlamaGuard Service (GPU)
```bash
cat <<EOF > llamaguard-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llamaguard
  namespace: nemo-guardrails
spec:
  replicas: 1
  selector:
    matchLabels:
      app: llamaguard
  template:
    metadata:
      labels:
        app: llamaguard
    spec:
      nodeSelector:
        cloud.google.com/gke-accelerator: nvidia-tesla-t4
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      containers:
      - name: llamaguard
        image: $REGISTRY/llamaguard:latest
        ports:
        - containerPort: 8001
        env:
        - name: HUGGING_FACE_HUB_TOKEN
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: hf-token
        resources:
          requests:
            nvidia.com/gpu: 1
            cpu: 2000m
            memory: 8Gi
          limits:
            nvidia.com/gpu: 1
            cpu: 4000m
            memory: 16Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 120
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: llamaguard-service
  namespace: nemo-guardrails
spec:
  selector:
    app: llamaguard
  ports:
  - port: 80
    targetPort: 8001
  type: ClusterIP
EOF

kubectl apply -f llamaguard-deployment.yaml
```

### Step 4: Deploy Other Services
```bash
# Deploy Presidio Service
cat <<EOF > presidio-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: presidio
  namespace: nemo-guardrails
spec:
  replicas: 2
  selector:
    matchLabels:
      app: presidio
  template:
    metadata:
      labels:
        app: presidio
    spec:
      containers:
      - name: presidio
        image: $REGISTRY/presidio:latest
        ports:
        - containerPort: 5001
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: presidio-service
  namespace: nemo-guardrails
spec:
  selector:
    app: presidio
  ports:
  - port: 80
    targetPort: 5001
  type: ClusterIP
EOF

kubectl apply -f presidio-deployment.yaml

# Deploy Content Safety Service
cat <<EOF > content-safety-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: content-safety
  namespace: nemo-guardrails
spec:
  replicas: 2
  selector:
    matchLabels:
      app: content-safety
  template:
    metadata:
      labels:
        app: content-safety
    spec:
      containers:
      - name: content-safety
        image: $REGISTRY/content-safety:latest
        ports:
        - containerPort: 5002
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: content-safety-service
  namespace: nemo-guardrails
spec:
  selector:
    app: content-safety
  ports:
  - port: 80
    targetPort: 5002
  type: ClusterIP
EOF

kubectl apply -f content-safety-deployment.yaml

# Deploy Jailbreak Detection Service
cat <<EOF > jailbreak-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jailbreak-detection
  namespace: nemo-guardrails
spec:
  replicas: 2
  selector:
    matchLabels:
      app: jailbreak-detection
  template:
    metadata:
      labels:
        app: jailbreak-detection
    spec:
      containers:
      - name: jailbreak-detection
        image: $REGISTRY/jailbreak-detection:latest
        ports:
        - containerPort: 1337
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: jailbreak-service
  namespace: nemo-guardrails
spec:
  selector:
    app: jailbreak-detection
  ports:
  - port: 80
    targetPort: 1337
  type: ClusterIP
EOF

kubectl apply -f jailbreak-deployment.yaml

# Deploy Fact Checking Service
cat <<EOF > factcheck-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: factcheck
  namespace: nemo-guardrails
spec:
  replicas: 2
  selector:
    matchLabels:
      app: factcheck
  template:
    metadata:
      labels:
        app: factcheck
    spec:
      containers:
      - name: factcheck
        image: $REGISTRY/factcheck:latest
        ports:
        - containerPort: 5000
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 1000m
            memory: 2Gi
---
apiVersion: v1
kind: Service
metadata:
  name: factcheck-service
  namespace: nemo-guardrails
spec:
  selector:
    app: factcheck
  ports:
  - port: 80
    targetPort: 5000
  type: ClusterIP
EOF

kubectl apply -f factcheck-deployment.yaml
```

## Phase 4: Expose Services

### Step 1: Create Load Balancer
```bash
# Create ingress for external access
cat <<EOF > ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nemo-guardrails-ingress
  namespace: nemo-guardrails
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "nemo-guardrails-ip"
    networking.gke.io/managed-certificates: "nemo-guardrails-ssl"
spec:
  rules:
  - host: guardrails.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nemo-main-service
            port:
              number: 80
      - path: /llamaguard
        pathType: Prefix
        backend:
          service:
            name: llamaguard-service
            port:
              number: 80
      - path: /presidio
        pathType: Prefix
        backend:
          service:
            name: presidio-service
            port:
              number: 80
      - path: /content-safety
        pathType: Prefix
        backend:
          service:
            name: content-safety-service
            port:
              number: 80
      - path: /jailbreak
        pathType: Prefix
        backend:
          service:
            name: jailbreak-service
            port:
              number: 80
      - path: /factcheck
        pathType: Prefix
        backend:
          service:
            name: factcheck-service
            port:
              number: 80
EOF

# Reserve static IP
gcloud compute addresses create nemo-guardrails-ip --global

# Create managed SSL certificate
cat <<EOF > ssl-cert.yaml
apiVersion: networking.gke.io/v1
kind: ManagedCertificate
metadata:
  name: nemo-guardrails-ssl
  namespace: nemo-guardrails
spec:
  domains:
    - guardrails.yourdomain.com
EOF

kubectl apply -f ssl-cert.yaml
kubectl apply -f ingress.yaml
```

### Step 2: Setup Internal Load Balancer (Optional)
```bash
# For internal communication between services
cat <<EOF > internal-lb.yaml
apiVersion: v1
kind: Service
metadata:
  name: nemo-main-internal
  namespace: nemo-guardrails
  annotations:
    cloud.google.com/load-balancer-type: "Internal"
spec:
  type: LoadBalancer
  selector:
    app: nemo-main
  ports:
  - port: 80
    targetPort: 8000
EOF

kubectl apply -f internal-lb.yaml
```

## Phase 5: Setup Monitoring

### Step 1: Deploy Prometheus and Grafana
```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --create-namespace \
    --set grafana.adminPassword=admin123

# Get Grafana service
kubectl get svc -n monitoring
```

### Step 2: Setup Basic Monitoring
```bash
# Create ServiceMonitor for scraping metrics
cat <<EOF > service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: nemo-guardrails-monitor
  namespace: nemo-guardrails
spec:
  selector:
    matchLabels:
      app: nemo-main
  endpoints:
  - port: web
    path: /metrics
EOF

kubectl apply -f service-monitor.yaml
```

## Phase 6: Auto-scaling Setup

### Step 1: Configure Horizontal Pod Autoscaler
```bash
# HPA for main service
kubectl autoscale deployment nemo-main \
    --cpu-percent=70 \
    --min=2 \
    --max=20 \
    --namespace=nemo-guardrails

# HPA for other services
kubectl autoscale deployment presidio \
    --cpu-percent=70 \
    --min=1 \
    --max=10 \
    --namespace=nemo-guardrails

kubectl autoscale deployment content-safety \
    --cpu-percent=70 \
    --min=1 \
    --max=10 \
    --namespace=nemo-guardrails

kubectl autoscale deployment jailbreak-detection \
    --cpu-percent=70 \
    --min=1 \
    --max=10 \
    --namespace=nemo-guardrails

kubectl autoscale deployment factcheck \
    --cpu-percent=70 \
    --min=1 \
    --max=8 \
    --namespace=nemo-guardrails
```

### Step 2: Enable Cluster Autoscaler
```bash
# The cluster autoscaler is already enabled, but let's verify
gcloud container clusters describe $CLUSTER_NAME \
    --region=$REGION \
    --format="value(nodeConfig.machineType,autoscaling.enabled)"
```

## Verification and Testing

### Check Deployment Status
```bash
# Check all pods
kubectl get pods -n nemo-guardrails

# Check services
kubectl get services -n nemo-guardrails

# Check ingress
kubectl get ingress -n nemo-guardrails

# Get external IP
kubectl get ingress nemo-guardrails-ingress -n nemo-guardrails \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### Test Services
```bash
# Get the external IP
EXTERNAL_IP=$(kubectl get ingress nemo-guardrails-ingress -n nemo-guardrails \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test main service
curl http://$EXTERNAL_IP/

# Test specific services (once they're properly configured with paths)
curl http://$EXTERNAL_IP/presidio/health
curl http://$EXTERNAL_IP/content-safety/health
```

## Maintenance Commands

### View Logs
```bash
# View logs for specific service
kubectl logs -f deployment/nemo-main -n nemo-guardrails

# View logs for all services
kubectl logs -f -l app=nemo-main -n nemo-guardrails
```

### Scale Services
```bash
# Scale specific deployment
kubectl scale deployment nemo-main --replicas=5 -n nemo-guardrails

# Check scaling status
kubectl get hpa -n nemo-guardrails
```

### Update Services
```bash
# Update image
kubectl set image deployment/nemo-main \
    nemo-main=$REGISTRY/nemo-guardrails:v2 \
    -n nemo-guardrails

# Check rollout status
kubectl rollout status deployment/nemo-main -n nemo-guardrails

# Rollback if needed
kubectl rollout undo deployment/nemo-main -n nemo-guardrails
```

### Cleanup
```bash
# Delete specific resources
kubectl delete namespace nemo-guardrails

# Delete cluster
gcloud container clusters delete $CLUSTER_NAME --region=$REGION

# Delete other resources
gcloud redis instances delete guardrails-cache --region=$REGION
gsutil -m rm -r gs://$PROJECT_ID-guardrails-models
gcloud compute addresses delete nemo-guardrails-ip --global
```

## Cost Optimization Tips

1. **Use Preemptible Nodes**: Already configured for non-GPU workloads
2. **Enable Cluster Autoscaler**: Scales down unused nodes
3. **Set Resource Limits**: Prevents resource waste
4. **Use HPA**: Scales pods based on usage
5. **Monitor Usage**: Use GCP billing alerts

## Security Best Practices

1. **Private Cluster**: Nodes have no public IPs
2. **Network Policies**: Restrict pod-to-pod communication
3. **RBAC**: Limit service account permissions  
4. **Secrets Management**: Use Kubernetes secrets for sensitive data
5. **Image Security**: Scan images for vulnerabilities

## Troubleshooting

### Common Issues
```bash
# Check pod status
kubectl describe pod <pod-name> -n nemo-guardrails

# Check events
kubectl get events -n nemo-guardrails --sort-by=.metadata.creationTimestamp

# Check resource usage
kubectl top pods -n nemo-guardrails
kubectl top nodes
```

### GPU Issues
```bash
# Check GPU driver installation
kubectl get pods -n kube-system | grep nvidia

# Check GPU availability
kubectl describe nodes | grep nvidia.com/gpu
```

This deployment approach gives you a production-ready NeMo Guardrails infrastructure on GCP without requiring Terraform knowledge!