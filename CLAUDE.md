# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Garak Guardrails Platform**, an enterprise deployment of NVIDIA's NeMo Guardrails with proprietary enhancements for production security and monitoring. The repository contains:

- **NeMo Guardrails submodule**: The open-source NVIDIA/NeMo-Guardrails framework for defensive AI safety
- **Garak submodule**: The open-source NVIDIA/Garak LLM vulnerability scanner for offensive security testing
- **Custom deployment configurations**: Docker, Kubernetes, and GCP deployment manifests
- **Proprietary monitoring**: Custom monitoring dashboard and control API
- **Security enhancements**: Production-ready security configurations
- **Comprehensive testing**: Integration, security, and performance test suites

## Development Environment Setup

### Prerequisites
- Python 3.9+ 
- Docker 20.10+
- Kubernetes 1.24+ (for deployments)
- Google Cloud SDK (for GCP deployments)

### Initial Setup
```bash
# Clone with submodules
git clone --recursive [repository-url]
cd garak-guardrails-platform

# Set up environment
cp .env.example .env
# Edit .env with your credentials
source .env

# Install dependencies (NeMo Guardrails)
cd nemo-guardrails
pip install -e .[all]
cd ..

# Install Garak vulnerability scanner
cd garak
pip install -e .
cd ..

# Install additional platform dependencies
pip install -r requirements.txt
```

## Architecture

### Core Components

1. **NeMo Guardrails Core** (`nemo-guardrails/`): Submodule containing the defensive guardrails framework
2. **Garak Vulnerability Scanner** (`garak/`): Submodule containing the offensive security testing toolkit
3. **Deployment Layer** (`deployments/`): Docker images and Kubernetes manifests
4. **Configuration Management** (`configs/`): Environment-specific guardrail configurations
5. **Monitoring System** (`monitoring/`): Custom Streamlit dashboard and control API
6. **Testing Framework** (`testing/`): Comprehensive test suites for validation

### Service Architecture
The platform runs as a microservices architecture with:
- **Main NeMo Guardrails Service** (port 8000): Primary API endpoint
- **Jailbreak Detection Service** (port 1337): Specialized jailbreak detection
- **Content Safety Service** (port 5002): Content moderation
- **Sensitive Data Detection Service** (port 5001): PII detection using Presidio
- **LLaMA Guard Service** (port 8001): Additional content safety validation

## Common Development Commands

### Running Locally
```bash
# Start all services with Docker Compose
docker-compose up -d

# Start lightweight version (fewer services)
docker-compose -f docker-compose.light.yml up -d

# Start monitoring dashboard
cd monitoring
streamlit run app.py
```

### Testing
```bash
# Run all dashboard tests
cd testing/dashboard_tests
python3 run_all_tests.py

# Run specific test modules
python3 -m pytest test_smoke.py -v
python3 -m pytest test_api_integration.py -v
python3 -m pytest test_guardrails.py -v

# Run local integration tests
python3 run_local_tests.py

# Run GCP deployment tests (requires GCP access)
python3 run_gcp_tests.py
```

### NeMo Guardrails Development
```bash
# Run NeMo Guardrails tests (from nemo-guardrails directory)
cd nemo-guardrails
python3 -m pytest tests/ -v

# Run specific NeMo test categories
python3 -m pytest tests/test_jailbreak_actions.py -v
python3 -m pytest tests/test_content_safety_actions.py -v

# Install in development mode
pip install -e .[all]

# Run linting and formatting
black nemoguardrails/
pylint nemoguardrails/
```

### Configuration Management
```bash
# Validate configuration files
nemoguardrails validate --config configs/production/main/

# Test configuration with sample inputs
nemoguardrails chat --config configs/production/main/

# Generate configuration templates
nemoguardrails init --template production

### Garak Vulnerability Testing
```bash
# Run basic vulnerability scan against API endpoint
cd garak
python -m garak --model-type rest --model-name api.garaksecurity.com/v1/chat/completions

# Run specific probe categories
python -m garak --probes promptinject,jailbreak --model-type rest --model-name api.garaksecurity.com/v1/chat/completions

# Run comprehensive security assessment
python -m garak --config configs/broad.yaml --model-type rest --model-name api.garaksecurity.com/v1/chat/completions

# Analyze results
python -m garak.analyze.analyze_log garak_runs/
```

## Deployment Commands

### Local Development Deployment
```bash
# Deploy lightweight local version
./deployments/scripts/deploy-light.sh

# Deploy with full monitoring
docker-compose up -d
```

### Production Deployment
```bash
# Deploy to GCP with HTTPS
cd deployments
./scripts/deploy.sh
# Select option 1 for HTTPS Production Deployment

# Deploy security-focused version
cd deployments
./scripts/deploy.sh  
# Select option 3 for Security-focused Deployment
```

### Kubernetes Operations
```bash
# Check deployment status
kubectl get pods
kubectl get services
kubectl get ingress

# View logs
kubectl logs -f deployment/nemo-guardrails
kubectl logs -f deployment/jailbreak-detection

# Scale services
kubectl scale deployment nemo-guardrails --replicas=3
```

## Configuration System

### Environment-Specific Configs
- `configs/production/main/`: Production guardrail configuration
- `configs/development/`: Development configurations  
- `configs/staging/`: Staging environment configurations

### Key Configuration Files
- `config.yml`: Main NeMo Guardrails configuration (models, instructions, rails)
- `prompts.yml`: Custom prompt templates
- `rails.co`: Colang flow definitions (when using Colang v2)

### Guardrail Categories
The platform supports multiple guardrail types:
- **Input Protection**: Jailbreak detection, injection detection, content safety, PII detection
- **Output Validation**: Self-check output, hallucination detection
- **Content Safety**: Harmful content filtering, sensitive data anonymization

## Monitoring and Control

### Dashboard Access
```bash
# Start monitoring dashboard
cd monitoring
streamlit run app.py
# Access at http://localhost:8501
```

### Control API
```bash
# Start control API server
cd monitoring  
python3 control_api.py
# API available at http://localhost:8090
```

### Key Monitoring Features
- Real-time service health monitoring
- Dynamic guardrail enable/disable
- Live configuration editing
- Guardrail testing interface
- Metrics and analytics

## File Structure Patterns

### Adding New Guardrails
1. Create guardrail implementation in `nemo-guardrails/nemoguardrails/actions/`
2. Add configuration in `configs/production/main/config.yml`
3. Add tests in `testing/dashboard_tests/`
4. Update monitoring dashboard categories in `monitoring/app.py`

### Adding New Services
1. Create Dockerfile in `deployments/dockerfiles/`
2. Add service to `docker-compose.yml`
3. Add Kubernetes manifests in `deployments/k8s-manifests/`
4. Add health check endpoints
5. Update monitoring configuration

## Testing Patterns

### Integration Tests
Located in `testing/dashboard_tests/`, these test the full stack:
- API integration (`test_api_integration.py`)
- Guardrail functionality (`test_guardrails.py`)
- Security features (`test_*_security*.py`)
- Deployment validation (`test_*_deployment.py`)

### Running Test Suites
- Tests automatically handle service unavailability (expected in some environments)
- Real failures vs. service unavailability are distinguished
- Use `run_all_tests.py` for comprehensive testing

## Security Considerations

- **No secrets in code**: Use `.env` files or Kubernetes secrets
- **Container security**: All containers run as non-root users
- **Network security**: Services communicate over internal networks
- **Input validation**: All inputs are validated through multiple guardrail layers
- **Output sanitization**: All outputs are checked for harmful content

## Troubleshooting

### Common Issues
- **Service startup failures**: Check Docker daemon and port availability
- **Configuration errors**: Validate YAML syntax and required fields
- **Permission errors**: Ensure proper file permissions for config files
- **Memory issues**: NeMo Guardrails can be memory-intensive; monitor resource usage

### Debug Commands
```bash
# Check service logs
docker-compose logs nemo-guardrails
docker-compose logs jailbreak-detection

# Validate configurations
nemoguardrails validate --config configs/production/main/

# Test individual guardrails
nemoguardrails chat --config configs/production/main/ --verbose
```