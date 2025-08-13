# Garak Guardrails Platform

Enterprise deployment of NeMo Guardrails with proprietary enhancements for production security and monitoring.

## 📄 License

This software is licensed under the **Garak Guardrails Platform Enterprise Edition (EE) License**.

- **Proprietary Code**: All code outside of submodules is proprietary to Garak Inc. and requires a valid Enterprise subscription for production use.
- **Open Source Components**: The `nemo-guardrails/` and `garak/` submodules retain their original Apache 2.0 licenses.
- **Development Use**: You may copy and modify the Software for development and testing purposes without a subscription.

See [LICENSE](LICENSE) for full terms. For licensing inquiries, contact legal@garaksecurity.com.

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
   git clone --recursive [your-private-repo-url]
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

This is a private repository. For contributions, please contact the maintainers.

## 📞 Support

For issues or questions, please contact the platform team.

---

**Version**: 1.0.0  
**Last Updated**: August 2025  
**Maintainers**: Garak Security Team