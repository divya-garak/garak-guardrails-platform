# NeMo Guardrails GCP Deployment Plan

## Executive Summary

This document outlines a comprehensive plan to deploy all NeMo Guardrails services on Google Cloud Platform (GCP), providing a scalable, secure, and cost-effective infrastructure for AI safety and content moderation services.

## 1. Service Inventory & Analysis

### 1.1 Core Guardrail Services
Based on analysis of the current codebase, we have identified the following deployable services:

#### **Tier 1: Core NeMo Services**
- **Main NeMo Guardrails Service** (Port 8000)
  - Primary guardrails engine with configurable policies
  - CPU-intensive, stateless
  - Horizontal scaling required
  
- **Comprehensive Guardrails Service** (Port 8004)
  - Full-featured configuration with all rails enabled
  - Higher resource requirements
  - Batch processing capabilities

#### **Tier 2: Specialized Detection Services**
- **Jailbreak Detection Service** (Port 1337)
  - ML-based detection of prompt injection attempts
  - GPU-accelerated heuristics available
  - Real-time response required
  
- **Content Safety Service** (Port 5002)
  - Multi-model content moderation
  - Toxic content, hate speech, harmful content detection
  - CPU/GPU hybrid workload
  
- **Sensitive Data Detection (Presidio)** (Port 5001)
  - PII and sensitive information detection
  - GDPR/CCPA compliance focused
  - CPU-intensive, regex + ML models

#### **Tier 3: AI Model Services** 
- **LlamaGuard Service** (Port 8001)
  - Meta's LlamaGuard model for content safety
  - **GPU Required** (NVIDIA T4/V100/A100)
  - High memory requirements (16GB+ VRAM)
  
- **Fact Checking Service (AlignScore)** (Port 5000)
  - Factual accuracy verification
  - CPU-intensive, moderate memory
  - Optional GPU acceleration

#### **Tier 4: Monitoring & Management**
- **Monitoring Dashboard**
  - Real-time metrics and alerts
  - Service health monitoring
  - Configuration management interface

#### **Additional Library Services**
- **ActiveFence Integration** - Third-party content moderation
- **Clavata AI Detection** - AI-generated content detection  
- **AutoAlign** - Alignment verification
- **Fiddler AI** - Model monitoring and validation
- **PatronusAI** - Advanced AI safety checks
- **PrivateAI** - Privacy-focused data detection
- **Prompt Security** - Advanced prompt injection detection
- **Topic Safety** - Topic-based content filtering
- **Hallucination Detection** - AI hallucination identification
- **Injection Detection** - SQL/XSS/Template injection detection

## 2. GCP Architecture Design

### 2.1 Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Internet                                │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Cloud Load Balancer                          │
│                    + Cloud Armor (WAF)                          │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│              API Gateway (Cloud Endpoints)                      │
│           Authentication, Rate Limiting, Monitoring             │
└─────────────────┬───────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                   GKE Cluster (Regional)                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Istio Service Mesh                       ││
│  │                  Traffic Management                         ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   CPU Node Pool │  │  GPU Node Pool  │  │ Monitoring Pool │ │
│  │                 │  │                 │  │                 │ │
│  │ • Core NeMo     │  │ • LlamaGuard    │  │ • Prometheus    │ │
│  │ • Jailbreak     │  │ • Content AI    │  │ • Grafana       │ │
│  │ • Presidio      │  │ • ML Models     │  │ • Alertmanager  │ │
│  │ • Fact Check    │  │                 │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────┐
│                    Supporting Services                          │
│                                                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │Cloud Storage│ │Secret Manager│ │ Memorystore │ │Cloud SQL    ││
│ │Model Files  │ │ API Keys    │ │   Redis     │ │Logs/Metrics ││
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Service Deployment Strategy

#### **Google Kubernetes Engine (GKE) - Primary Platform**
- **Regional cluster** for high availability
- **Multiple node pools** for different workload types
- **Cluster autoscaler** for cost optimization
- **Workload Identity** for secure service access

#### **Node Pool Configuration**

**CPU-Optimized Pool (e2-standard-4 to e2-standard-8)**
- Core NeMo Guardrails services
- Jailbreak detection (CPU mode)
- Presidio sensitive data detection
- Fact checking service
- Supporting services

**GPU-Enabled Pool (n1-standard-4 + NVIDIA T4/V100)**
- LlamaGuard service
- Advanced AI model services
- GPU-accelerated jailbreak detection
- Content safety ML models

**Memory-Optimized Pool (n2-highmem-2)**
- Large model loading
- Batch processing services
- Data-intensive operations

## 3. Infrastructure Components

### 3.1 Compute Resources

#### **Google Kubernetes Engine (GKE)**
```yaml
Cluster Specifications:
- Type: Regional (multi-zone)
- Version: Latest stable GKE version
- Network: VPC-native with alias IPs
- Security: Private cluster with authorized networks
- Addons: 
  - HTTP Load Balancing
  - Network Policy
  - Istio Service Mesh
  - Cloud Monitoring
```

#### **Node Pools**
```yaml
CPU Pool:
  Machine Type: e2-standard-4 (4 vCPU, 16GB RAM)
  Disk: 100GB SSD persistent disk
  Autoscaling: 1-10 nodes
  Preemptible: Mixed (50% preemptible for cost optimization)

GPU Pool:
  Machine Type: n1-standard-4 + NVIDIA T4
  GPU Count: 1 T4 per node
  Disk: 200GB SSD persistent disk  
  Autoscaling: 0-5 nodes (scales to zero when not needed)
  Preemptible: No (for model consistency)

Memory Pool:
  Machine Type: n2-highmem-2 (2 vCPU, 16GB RAM)
  Disk: 50GB SSD persistent disk
  Autoscaling: 1-3 nodes
  Preemptible: Yes (cost optimization)
```

### 3.2 Storage Solutions

#### **Cloud Storage**
- **Model Repository**: Store ML models, embeddings, configurations
- **Backup Storage**: Configuration backups, logs archival
- **Static Assets**: Documentation, web assets

#### **Persistent Disks**
- **Regional SSD**: For database storage, critical data
- **Standard Persistent Disk**: For logs, temporary storage

#### **Memorystore (Redis)**
- **Caching Layer**: API response caching, session storage
- **Rate Limiting**: Distributed rate limiting data
- **Configuration Cache**: Hot configuration storage

### 3.3 Networking

#### **VPC Network**
- **Private GKE cluster** with no public IPs on nodes
- **Authorized networks** for cluster access
- **Firewall rules** for micro-segmentation
- **Cloud NAT** for outbound internet access

#### **Load Balancing**
- **Global HTTP(S) Load Balancer** for public traffic
- **Internal Load Balancer** for service-to-service communication
- **Cloud Armor** for DDoS protection and WAF

#### **API Gateway**
- **Cloud Endpoints** for API management
- **Authentication** (API keys, OAuth, JWT)
- **Rate limiting** and quota management
- **Request/response transformation**

## 4. Service Deployment Specifications

### 4.1 Core Services Deployment

#### **Main NeMo Guardrails Service**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nemo-main
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: nemo-main
        image: gcr.io/PROJECT/nemo-guardrails:latest
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key
```

#### **LlamaGuard GPU Service**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llamaguard
spec:
  replicas: 2
  template:
    spec:
      nodeSelector:
        cloud.google.com/gke-accelerator: nvidia-tesla-t4
      containers:
      - name: llamaguard
        image: gcr.io/PROJECT/llamaguard:latest
        resources:
          requests:
            nvidia.com/gpu: 1
            cpu: 2000m
            memory: 8Gi
          limits:
            nvidia.com/gpu: 1
            cpu: 4000m
            memory: 16Gi
```

### 4.2 Auto-scaling Configuration

#### **Horizontal Pod Autoscaler (HPA)**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nemo-main-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nemo-main
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### **Vertical Pod Autoscaler (VPA)**
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: nemo-main-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nemo-main
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: nemo-main
      maxAllowed:
        cpu: 4000m
        memory: 8Gi
```

## 5. Security Architecture

### 5.1 Identity and Access Management

#### **Service Accounts**
- **GKE Service Account**: Minimal permissions for cluster operations
- **Workload Identity**: Secure pod-to-GCP service authentication
- **Application Service Accounts**: Least-privilege access per service

#### **Secret Management**
- **Google Secret Manager**: Store API keys, certificates, tokens
- **Kubernetes Secrets**: Runtime secret injection
- **Automatic secret rotation**: Regular key rotation policies

### 5.2 Network Security

#### **Private Cluster**
- No public IPs on worker nodes
- Authorized networks for control plane access
- Private Google Access for GCP services

#### **Pod Security Standards**
```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

#### **Network Policies**
- Micro-segmentation between services
- Ingress/egress traffic control
- Default deny-all with explicit allow rules

### 5.3 Compliance and Governance

#### **Data Protection**
- **Encryption at rest**: All persistent disks encrypted
- **Encryption in transit**: TLS 1.3 for all communications
- **Data residency**: Region-specific deployment for compliance

#### **Audit Logging**
- **Cloud Audit Logs**: All administrative actions logged
- **Application Logs**: Structured logging with sensitive data redaction
- **Access Logs**: All API access logged and monitored

## 6. Monitoring and Observability

### 6.1 Metrics and Monitoring

#### **Google Cloud Monitoring Integration**
- **Infrastructure metrics**: CPU, memory, disk, network
- **Kubernetes metrics**: Pod health, cluster status
- **Application metrics**: Custom business metrics
- **SLI/SLO monitoring**: Service level objectives tracking

#### **Prometheus Stack** (On-cluster)
```yaml
Components:
- Prometheus Server: Metrics collection and storage
- Grafana: Visualization and dashboards
- Alertmanager: Alert routing and notification
- Node Exporter: Host-level metrics
- Kube-state-metrics: Kubernetes object metrics
```

#### **Custom Dashboards**
- **Service Health Dashboard**: All guardrail services status
- **Performance Dashboard**: Latency, throughput, error rates
- **Resource Utilization**: CPU, memory, GPU usage
- **Business Metrics**: API usage, detection rates, model accuracy

### 6.2 Logging Strategy

#### **Centralized Logging**
- **Cloud Logging**: Structured JSON logs
- **Log aggregation**: Multi-service log correlation
- **Log retention**: 30 days hot, 1 year archive
- **Sensitive data redaction**: PII removal from logs

#### **Log Categories**
- **Access Logs**: API requests, authentication events
- **Application Logs**: Service-specific operational logs
- **Audit Logs**: Administrative actions, configuration changes
- **Error Logs**: Exceptions, failures, performance issues

### 6.3 Alerting and Incident Response

#### **Alert Hierarchy**
```yaml
Critical (P0):
  - Service down (>5 minutes)
  - High error rate (>5% for >5 minutes)
  - GPU service failures
  - Security incidents

High (P1):
  - High latency (>2s p95 for >10 minutes)
  - Resource exhaustion warnings
  - Scaling failures
  - Certificate expiration (7 days)

Medium (P2):
  - Performance degradation
  - Non-critical service issues
  - Capacity planning warnings

Low (P3):
  - Information alerts
  - Maintenance notifications
```

#### **Notification Channels**
- **PagerDuty**: Critical and high-priority alerts
- **Slack**: All alert levels for team visibility
- **Email**: Summary reports and low-priority alerts
- **SMS**: Critical alerts for on-call rotation

## 7. CI/CD Pipeline

### 7.1 Source Code Management

#### **Repository Structure**
```
nemo-guardrails-gcp/
├── src/                    # Application source code
├── docker/                 # Dockerfile configurations
├── k8s/                    # Kubernetes manifests
├── terraform/              # Infrastructure as Code
├── helm/                   # Helm charts
├── monitoring/             # Monitoring configurations
├── scripts/                # Deployment scripts
└── docs/                   # Documentation
```

#### **Branch Strategy**
- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: Feature development branches  
- **hotfix/***: Critical production fixes

### 7.2 Build Pipeline (Cloud Build)

#### **Build Triggers**
```yaml
# cloudbuild.yaml
steps:
# Build and test
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/nemo-guardrails:$COMMIT_SHA', '.']
  
# Security scanning
- name: 'gcr.io/cloud-builders/gcloud'  
  args: ['container', 'images', 'scan', 'gcr.io/$PROJECT_ID/nemo-guardrails:$COMMIT_SHA']
  
# Push to registry
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/nemo-guardrails:$COMMIT_SHA']
  
# Deploy to staging
- name: 'gcr.io/cloud-builders/gke-deploy'
  args: ['run', '--filename=k8s/', '--cluster=staging-cluster', '--location=us-central1']
```

#### **Multi-stage Builds**
- **Development**: Fast builds, debug symbols
- **Staging**: Production-like, with testing tools
- **Production**: Optimized, minimal attack surface

### 7.3 Deployment Strategy

#### **GitOps with ArgoCD**
- **Declarative deployments**: Infrastructure and applications as code
- **Automated sync**: Git repository as source of truth
- **Rollback capability**: Easy reversion to previous versions
- **Multi-environment**: Separate configs for dev/staging/prod

#### **Blue-Green Deployments**
- **Zero-downtime deployments**: Traffic switching between environments
- **Instant rollback**: Quick recovery from deployment issues
- **Canary deployments**: Gradual traffic shifting for risk mitigation

## 8. Cost Optimization Strategy

### 8.1 Resource Optimization

#### **Node Pool Strategies**
- **Preemptible instances**: 50-70% cost savings for fault-tolerant workloads
- **Committed use discounts**: 1-3 year commitments for predictable workloads
- **Regional persistent disks**: Cross-zone redundancy without snapshots

#### **Autoscaling Policies**
- **Cluster autoscaler**: Scale nodes based on pod resource requests
- **Pod autoscaling**: HPA and VPA for right-sizing
- **Schedule-based scaling**: Scale down during off-hours

#### **Resource Requests and Limits**
```yaml
resources:
  requests:
    cpu: 100m      # Minimum guaranteed
    memory: 256Mi
  limits:
    cpu: 500m      # Maximum allowed
    memory: 512Mi
```

### 8.2 Cost Monitoring

#### **Budget Alerts**
- **Monthly budget**: Set spending limits with alerts at 50%, 75%, 90%
- **Project-level budgets**: Separate budgets per environment
- **Service-level attribution**: Cost breakdown by service

#### **Resource Utilization Tracking**
- **Idle resource identification**: Underutilized nodes and pods
- **Right-sizing recommendations**: Optimize resource allocations
- **Waste reduction**: Remove unused resources automatically

### 8.3 Alternative Services for Cost Reduction

#### **Cloud Run** (For suitable workloads)
- **Serverless**: Pay only for requests
- **Auto-scaling**: Scales to zero when not in use
- **Suitable for**: Batch processing, infrequent services

#### **Cloud Functions** (For lightweight services)
- **Event-driven**: Perfect for webhooks, simple APIs
- **Automatic scaling**: No infrastructure management
- **Cost-effective**: Sub-second billing

## 9. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
**Week 1-2: Infrastructure Setup**
- [ ] GCP project creation and IAM setup
- [ ] VPC network and security configuration  
- [ ] GKE cluster deployment (CPU pool only)
- [ ] Basic monitoring setup (Cloud Monitoring)
- [ ] CI/CD pipeline foundation (Cloud Build)

**Week 3-4: Core Services**
- [ ] Main NeMo Guardrails service deployment
- [ ] Presidio service deployment
- [ ] Basic load balancer and API gateway
- [ ] Service health checks and basic monitoring
- [ ] Documentation and runbooks

### Phase 2: AI Services (Weeks 5-8)
**Week 5-6: GPU Infrastructure**
- [ ] GPU node pool setup and configuration
- [ ] LlamaGuard service deployment
- [ ] Content safety service deployment
- [ ] GPU monitoring and autoscaling

**Week 7-8: Advanced Detection**
- [ ] Jailbreak detection service (CPU and GPU modes)
- [ ] Fact checking service deployment
- [ ] Advanced monitoring dashboards
- [ ] Performance optimization

### Phase 3: Scale and Optimize (Weeks 9-12)
**Week 9-10: Production Readiness**
- [ ] Multi-region deployment preparation
- [ ] Advanced security hardening
- [ ] Comprehensive testing and load testing
- [ ] Disaster recovery procedures

**Week 11-12: Additional Services**
- [ ] Library services deployment (ActiveFence, Clavata, etc.)
- [ ] Advanced monitoring and alerting
- [ ] Cost optimization implementation  
- [ ] Performance tuning and optimization

### Phase 4: Operations and Maintenance (Ongoing)
**Continuous Activities**
- [ ] Security updates and patching
- [ ] Performance monitoring and optimization
- [ ] Cost analysis and optimization
- [ ] Service expansion and new feature deployment
- [ ] Incident response and troubleshooting

## 10. Success Metrics and KPIs

### 10.1 Technical Metrics
- **Availability**: 99.9% uptime SLA
- **Performance**: <200ms p95 response time
- **Scalability**: Handle 10x traffic spikes
- **Security**: Zero security incidents

### 10.2 Business Metrics  
- **Cost Efficiency**: <$X per 1M API calls
- **Service Adoption**: Number of integrated applications
- **Detection Accuracy**: False positive/negative rates
- **Time to Market**: Feature deployment cycle time

### 10.3 Operational Metrics
- **Mean Time to Recovery (MTTR)**: <30 minutes
- **Deployment Frequency**: Daily deployments capability
- **Change Failure Rate**: <5% of deployments require rollback
- **Lead Time**: Feature request to production <2 weeks

## 11. Risk Assessment and Mitigation

### 11.1 Technical Risks
**Risk**: GPU resource availability and cost
**Mitigation**: Multi-region deployment, reserved instances, fallback CPU modes

**Risk**: Model drift and accuracy degradation
**Mitigation**: Continuous monitoring, A/B testing, automated retraining

**Risk**: Service dependencies and cascading failures
**Mitigation**: Circuit breakers, graceful degradation, redundancy

### 11.2 Operational Risks
**Risk**: Team expertise and knowledge gaps
**Mitigation**: Training programs, documentation, external consulting

**Risk**: Vendor lock-in with GCP services
**Mitigation**: Containerized deployments, multi-cloud strategy, open standards

**Risk**: Compliance and regulatory changes
**Mitigation**: Regular compliance audits, flexible architecture, legal review

## 12. Conclusion

This comprehensive plan provides a robust, scalable, and cost-effective approach to deploying NeMo Guardrails services on GCP. The architecture leverages modern cloud-native technologies while maintaining security, observability, and operational excellence.

The phased implementation approach allows for iterative delivery, risk mitigation, and continuous improvement. With proper execution, this deployment will provide a world-class AI safety platform capable of serving enterprise-scale workloads with high availability and performance.

**Next Steps:**
1. Review and approve the architectural design
2. Provision GCP resources and begin Phase 1 implementation
3. Establish monitoring and alerting baselines
4. Begin team training and documentation development
5. Plan for pilot customer onboarding and feedback collection