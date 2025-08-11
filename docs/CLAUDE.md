# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NeMo Guardrails is an open-source toolkit for easily adding programmable guardrails to LLM-based conversational applications. It enables developers to add control mechanisms like input/output rails, dialog rails, retrieval rails, and execution rails to guide and safeguard LLM interactions.

## Key Commands

### Development and Testing
- `poetry run pytest` - Run all tests
- `poetry run pytest tests/test_specific.py` - Run specific test file
- `poetry run pytest tests/ -k "test_name"` - Run tests matching pattern
- `poetry run pytest tests/ --import-mode importlib` - Run tests with import mode (used by tox)
- `make test` - Run unit tests (alias)
- `make test_coverage` - Run tests with coverage report
- `make test_watch` - Run tests in watch mode using pytest-watch
- `make test_profile` - Run tests with profiling enabled
- `make pre_commit` - Install and run pre-commit hooks (formatting, linting)
- `tox` - Run tests across multiple Python versions (3.9-3.12)

### CLI Usage
- `nemoguardrails chat --config path/to/config` - Start interactive chat session
- `nemoguardrails server --config path/to/configs` - Start guardrails server
- `nemoguardrails convert path/to/files` - Convert Colang files between versions
- `nemoguardrails eval` - Run evaluation tasks

### Documentation
- `make docs` - Build documentation using Sphinx

## Architecture Overview

### Core Components

1. **LLMRails** (`nemoguardrails/rails/llm/llmrails.py`) - Main entry point for guardrails functionality
2. **RailsConfig** (`nemoguardrails/rails/llm/config.py`) - Configuration management for guardrails
3. **Colang Runtime** - Two versions supported:
   - `nemoguardrails/colang/v1_0/` - Colang 1.0 (default)
   - `nemoguardrails/colang/v2_x/` - Colang 2.0 (beta)

### Configuration Structure

Guardrails configurations typically follow this structure:
```
config/
├── config.yml          # Main configuration (models, rails settings)
├── config.py           # Custom initialization code (optional)  
├── actions.py          # Custom Python actions (optional)
├── rails.co            # Colang rail definitions
├── prompts.yml         # Custom prompts (optional)
└── rails/              # Additional rail files
    ├── input.co
    ├── output.co
    └── dialog.co
```

### Built-in Libraries

The `nemoguardrails/library/` directory contains pre-built guardrails for:
- Jailbreak detection
- Content moderation (self-check, LlamaGuard, ActiveFence)
- Fact-checking and hallucination detection
- Sensitive data detection (Presidio)
- Topic safety controls

### Testing Structure

- Unit tests in `tests/` mirror the source structure
- Test configurations in `tests/test_configs/`
- Integration tests cover CLI, server, and library components
- Use `conftest.py` for shared test fixtures

## Development Notes

### Colang Files (.co)
- Colang is the domain-specific language for defining dialog flows and guardrails
- Files use `.co` extension
- Two versions: 1.0 (stable) and 2.0 (beta)
- Found throughout examples/ and library/ directories

### Python Version Support
- Supports Python 3.9-3.13 (excluding 3.9.7)
- Uses Poetry for dependency management
- Pre-commit hooks include: isort, black, trailing-whitespace, end-of-file-fixer, check-yaml, license insertion

### Key Dependencies
- FastAPI/Starlette for server functionality
- LangChain for LLM integrations
- Pydantic for configuration validation
- Typer for CLI interface

### Configuration Loading
- Configurations loaded from YAML files (`config.yml`)
- Support for environment variable substitution
- Multiple model support (OpenAI, HuggingFace, etc.)
- Optional custom initialization via `config.py`

### Server Architecture
- FastAPI-based server in `nemoguardrails/server/`
- Supports multiple configurations
- Built-in chat UI (can be disabled)
- REST API endpoints for chat completions

### Evaluation Framework
- Built-in evaluation tools in `nemoguardrails/eval/`
- Support for topical rails, fact-checking, moderation testing
- CLI evaluation commands available

## Optional Dependencies and Extras

The project supports several optional extras that can be installed based on your needs:
- `poetry install -E sdd` - Sensitive data detection with Presidio
- `poetry install -E eval` - Evaluation tools (tqdm, numpy, streamlit, tornado)
- `poetry install -E openai` - OpenAI provider support
- `poetry install -E gcp` - Google Cloud Platform text moderation
- `poetry install -E tracing` - OpenTelemetry tracing support
- `poetry install -E nvidia` - NVIDIA AI Endpoints support
- `poetry install -E jailbreak` - YARA-based jailbreak detection
- `poetry install -E all` - Install all optional dependencies

## Project Structure Notes

### Key Directories
- `nemoguardrails/` - Main source code
- `tests/` - Unit and integration tests (mirrors source structure)
- `examples/` - Example configurations and scripts
- `docs/` - Documentation source files
- `library/` - Pre-built guardrail components for common use cases
- `dashboard_tests/` - Deployment and integration testing
- `k8s-deployments/` - Kubernetes deployment configurations

## Session Progress Log (August 8, 2025)

### Completed Tasks ✅

#### 1. Docker Configuration and Local Testing
- **Updated Dockerfile.full** with working NeMo Guardrails configuration from `server_configs/`
- **Fixed missing dependency**: Added `langchain-openai` package to resolve HTTP 500 errors
- **Successfully containerized** the working configuration with self-check flows and jailbreak detection
- **Local deployment validated** on port 8050 with full test suite

#### 2. Test Suite Validation
- **26/26 tests passing** locally:
  - API Integration: 7/7 tests ✅
  - Comprehensive Security: 12/12 tests ✅  
  - Endpoint Validation: 7/7 tests ✅
- **Security features confirmed working**:
  - Jailbreak detection blocking malicious prompts
  - Content safety filtering active
  - Normal conversations working properly
  - All API endpoints responsive

#### 3. GCP Deployment Configuration
- **Updated deploy_gcp_production_security.sh** with hardcoded secrets (per user request)
- **Configured for api.garaksecurity.com** domain
- **Set up garak-shield project** integration
- **Prepared Kubernetes manifests** with security configurations

### Current Status ⚠️

#### GCP Deployment In Progress
- **Docker image built and pushed** to GCR successfully
- **GKE cluster exists** and is running
- **Redis deployment successful** (1/1 pods running)
- **NeMo deployment having issues**: ImagePullBackOff errors with GCR image

### Next Steps 🎯

#### Immediate Actions Required
1. **Fix ImagePull issue**:
   ```bash
   # Switch to Artifact Registry (more reliable)
   docker build -f Dockerfile.full -t us-central1-docker.pkg.dev/garak-shield/nemo-repo/nemo-guardrails-secure:latest .
   docker push us-central1-docker.pkg.dev/garak-shield/nemo-repo/nemo-guardrails-secure:latest
   
   # Update deployment to use Artifact Registry image
   kubectl patch deployment nemo-guardrails-secure -p '{"spec":{"template":{"spec":{"containers":[{"name":"nemo-guardrails","image":"us-central1-docker.pkg.dev/garak-shield/nemo-repo/nemo-guardrails-secure:latest"}]}}}}'
   ```

2. **Verify deployment health**:
   ```bash
   kubectl get pods -w
   kubectl wait --for=condition=available deployment/nemo-guardrails-secure --timeout=600s
   ```

3. **Get external IP and test**:
   ```bash
   kubectl get service nemo-guardrails-secure-service
   # Test: curl http://EXTERNAL_IP/health
   ```

#### Final DNS Configuration
4. **Update DNS** to point `api.garaksecurity.com` to the external IP
5. **Run production validation tests** against the live deployment

### Key Files Modified
- **Dockerfile.full**: Added langchain-openai, configured server_configs copying
- **deploy_gcp_production_security.sh**: Hardcoded secrets, configured for api.garaksecurity.com
- **Server configs**: Working configuration with self-check flows in `server_configs/main/`

### Commands for Quick Deployment Resume
```bash
# Resume GCP deployment from current state
cd /Users/divyachitimalla/NeMo-Guardrails
kubectl get pods  # Check current status
# Fix image issue and continue deployment as outlined above
```