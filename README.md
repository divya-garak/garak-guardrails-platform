# Garak Guardrails Platform

> **⚠️ PROPRIETARY SOFTWARE - PUBLIC REPOSITORY**
> 
> This is a **public repository** containing **proprietary software** owned by Garak Inc.
> While the code is publicly viewable for transparency and development purposes, it is NOT open source.
> Production use requires a valid Garak Enterprise Edition subscription.

Enterprise deployment of NeMo Guardrails with proprietary enhancements for production security and monitoring.

## 📄 License Notice

**This is proprietary software licensed under the Garak Guardrails Platform Enterprise Edition (EE) License.**

- ❌ **NOT Open Source**: The code in this repository (except submodules) is proprietary to Garak Inc.
- ✅ **Public Viewing**: Code is made publicly available for transparency, security auditing, and evaluation
- 💼 **Commercial Use**: Requires a valid Enterprise subscription for production deployment
- 🔬 **Development Use**: Free for development and testing purposes only
- 📦 **Submodules**: `nemo-guardrails/` and `garak/` retain their original Apache 2.0 licenses

See [LICENSE](LICENSE) for full legal terms. For licensing inquiries: legal@garaksecurity.com

## 🏗️ Architecture

This repository contains our proprietary deployment and configuration for NeMo Guardrails, using the open-source [NVIDIA/NeMo-Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) as a submodule.

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Kubernetes 1.24+
- Google Cloud SDK
- Python 3.9+

### Setup

1. **Clone with submodules:**
   ```bash
   git clone --recursive https://github.com/divya-garak/garak-guardrails-platform.git
   cd garak-guardrails-platform
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   source .env
   ```

3. **Initialize platform:**
   ```bash
   ./scripts/setup.sh
   ```

4. **Deploy to production:**
   ```bash
   ./scripts/deploy.sh production
   ```

## 📁 Repository Structure

```
.
├── nemo-guardrails/        # NVIDIA NeMo-Guardrails (submodule)
├── deployments/           # Kubernetes & Docker configurations
│   ├── dockerfiles/       # Custom Docker images
│   ├── k8s-manifests/     # Kubernetes resources
│   └── scripts/           # Deployment automation
├── infrastructure/        # Cloud infrastructure (Terraform/GCP)
│   ├── terraform/         # IaC definitions
│   ├── gke/              # GKE configurations
│   └── scripts/          # Infrastructure automation
├── testing/              # Test suites
│   ├── integration/      # API integration tests
│   ├── security/         # Security validation tests
│   └── performance/      # Load and performance tests
├── configs/              # Application configurations
│   ├── production/       # Production configs
│   ├── staging/          # Staging configs
│   └── development/      # Development configs
├── monitoring/           # Custom monitoring solutions
│   ├── dashboard/        # Grafana dashboards
│   └── api/             # Monitoring API
├── docs/                # Documentation
│   ├── deployment/      # Deployment guides
│   ├── security/        # Security documentation
│   └── api/            # API documentation
└── scripts/            # Top-level automation scripts
```

## 🛡️ Security Features

- **Jailbreak Detection**: Multi-layer bypass prevention
- **Content Safety**: Harmful content filtering
- **Input/Output Validation**: Self-check flows
- **Secret Management**: Kubernetes secrets & environment variables
- **HTTPS/TLS**: Full encryption with Let's Encrypt

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available configuration options.

### Deployment Environments

- **Production**: Full security, monitoring, and scaling
- **Staging**: Pre-production testing
- **Development**: Local development with hot reload

## 📊 Monitoring

- **Health Endpoints**: `/health`, `/ready`, `/metrics`
- **Grafana Dashboards**: Real-time metrics visualization
- **Logging**: Structured JSON logging with correlation IDs
- **Tracing**: OpenTelemetry integration (optional)

## 🧪 Testing

```bash
# Run all tests
./scripts/test.sh all

# Run specific test suites
./scripts/test.sh integration
./scripts/test.sh security
./scripts/test.sh performance
```

## 📚 Documentation

- [Deployment Guide](docs/deployment/README.md)
- [Security Guidelines](docs/security/README.md)
- [API Reference](docs/api/README.md)
- [Troubleshooting](docs/troubleshooting/README.md)

## 🔒 Security

This repository follows strict security practices:

- No secrets in code (use `.env` or secret management)
- Automated secret scanning on every commit
- Regular dependency updates
- Security-first Docker images
- Non-root container execution

## 📝 License

This repository contains proprietary code. All rights reserved.

The included NeMo-Guardrails submodule is licensed under Apache 2.0 by NVIDIA Corporation.

## 🤝 Contributing

While this repository is public for transparency, contributions are managed internally by Garak Inc.
For bug reports or security issues, please email: security@garaksecurity.com

## 📞 Support

- **Enterprise Support**: Available for licensed customers
- **Documentation**: https://docs.getgarak.com
- **Sales Inquiries**: sales@garaksecurity.com
- **Security Issues**: security@garaksecurity.com

---

## © Copyright Notice

**Copyright (c) 2025 Garak Inc. All Rights Reserved.**

This repository contains proprietary software owned by Garak Inc. The code is made publicly 
available for transparency and evaluation purposes only. Any use in production requires a 
valid Garak Enterprise Edition subscription.

**Version**: 1.0.0  
**Last Updated**: January 2025  
**Maintainers**: Garak Security Team  
**Repository**: https://github.com/divya-garak/garak-guardrails-platform