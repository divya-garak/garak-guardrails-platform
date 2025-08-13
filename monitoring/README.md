# Dynamic Provider Configuration System

This directory contains a comprehensive dynamic provider configuration system for NeMo Guardrails that allows users to configure any LLM provider with their API keys via API endpoints instead of hardcoded configuration.

## Overview

The system provides:

- **Dynamic Provider Management**: Register and manage LLM provider configurations at runtime
- **API Key Security**: Secure handling of API keys without hardcoding in configuration files
- **Multi-Provider Support**: OpenAI, Anthropic, Azure, Hugging Face, and more
- **Configuration Migration**: Tools to migrate existing hardcoded configurations
- **NeMo Integration**: Seamless integration with NeMo Guardrails configuration system
- **Production Ready**: Deployment configurations for Docker and Kubernetes

## Architecture

### Core Components

1. **`dynamic_provider.py`**: Core provider management system
   - Provider registration and credential management
   - Configuration validation and resolution
   - Support for multiple provider types

2. **`provider_api.py`**: REST API endpoints for provider management
   - CRUD operations for provider configurations
   - Configuration generation and testing
   - Provider validation and status checking

3. **`provider_extensions.py`**: Extended API endpoints
   - NeMo Guardrails integration endpoints
   - Provider activation/deactivation
   - Synchronization and status monitoring

4. **`nemo_integration.py`**: NeMo Guardrails integration layer
   - Configuration resolution and application
   - Backup and restore functionality
   - Validation and status checking

5. **`config_migrator.py`**: Configuration migration tools
   - Automated migration of legacy configurations
   - Analysis and planning tools
   - Validation and rollback support

6. **`control_api.py`**: Enhanced control API with provider support
   - Integrated provider management
   - Guardrail control with dynamic providers
   - Health monitoring and metrics

## API Endpoints

### Provider Management

- `GET /api/providers/supported` - Get supported providers
- `GET /api/providers/` - List all provider configurations
- `POST /api/providers/` - Create new provider configuration
- `GET /api/providers/{id}` - Get specific provider configuration
- `PUT /api/providers/{id}` - Update provider configuration
- `DELETE /api/providers/{id}` - Delete provider configuration
- `POST /api/providers/{id}/test` - Test provider configuration

### NeMo Integration

- `POST /api/providers/sync` - Sync all providers to NeMo config
- `POST /api/providers/{id}/activate` - Activate provider in NeMo
- `POST /api/providers/{id}/deactivate` - Deactivate provider from NeMo
- `GET /api/providers/status` - Get NeMo configuration status
- `GET /api/providers/{id}/generate-config` - Generate NeMo config

## Usage Examples

### 1. Register an OpenAI Provider

```bash
curl -X POST http://localhost:8090/api/providers/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "config_id": "my-openai-gpt4",
    "config": {
      "provider_name": "openai",
      "credentials": {
        "api_key": "sk-your-openai-key-here",
        "organization": "your-org-id"
      },
      "model_name": "gpt-4",
      "parameters": {
        "temperature": 0.7,
        "max_tokens": 1000
      }
    }
  }'
```

### 2. Register an Anthropic Provider

```bash
curl -X POST http://localhost:8090/api/providers/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "config_id": "my-anthropic-claude",
    "config": {
      "provider_name": "anthropic",
      "credentials": {
        "api_key": "sk-ant-your-anthropic-key-here"
      },
      "model_name": "claude-3-5-sonnet-20241022",
      "parameters": {
        "max_tokens": 1024,
        "temperature": 0.5
      }
    }
  }'
```

### 3. Activate Provider in NeMo Guardrails

```bash
curl -X POST http://localhost:8090/api/providers/my-openai-gpt4/activate
```

### 4. Synchronize All Providers

```bash
curl -X POST http://localhost:8090/api/providers/sync
```

## Configuration Schema

### Dynamic Provider Reference

Instead of hardcoded configurations:

```yaml
# Old way - hardcoded
models:
  - type: main
    engine: openai
    model: gpt-4
    parameters:
      api_key: sk-hardcoded-key  # Security risk!
```

Use dynamic provider references:

```yaml
# New way - dynamic
models:
  - type: main
    provider_config_id: "my-openai-gpt4"  # Resolved at runtime
```

### Full Configuration Example

```yaml
colang_version: "2.x"

models:
  # Multiple dynamic providers
  - type: main
    provider_config_id: "my-openai-gpt4"
  - type: main
    provider_config_id: "my-anthropic-claude"
  - type: main
    provider_config_id: "my-azure-gpt35"

rails:
  input:
    flows: ["self check input"]
  output:
    flows: ["self check output"]

metadata:
  supports_dynamic_providers: true
```

## Migration Tools

### Migrate Existing Configuration

```python
from monitoring.config_migrator import migrate_config_file

# Migrate a configuration file
result = migrate_config_file(
    input_path="configs/production/main/config.yml",
    backup=True
)

if result.success:
    print("Migration successful!")
    print(f"Changes: {result.changes}")
else:
    print(f"Migration failed: {result.errors}")
```

### Analyze Configuration

```python
from monitoring.config_migrator import ConfigMigrator

migrator = ConfigMigrator()
analysis = migrator.analyze_config(config)

print(f"Total models: {analysis['total_models']}")
print(f"Migration candidates: {len(analysis['migration_candidates'])}")
print(f"Hardcoded keys found: {len(analysis['hardcoded_keys'])}")
```

## Deployment

### Docker Compose

Use the enhanced Docker Compose configuration:

```bash
cd deployments
docker-compose -f docker-compose.dynamic-providers.yml up -d
```

### Kubernetes

Deploy the provider monitoring service:

```bash
kubectl apply -f deployments/k8s-manifests/provider-monitor-deployment.yaml
```

## Security Features

1. **API Key Encryption**: Credentials stored securely
2. **Environment Isolation**: Separate configurations per environment
3. **CORS Protection**: Configurable CORS policies
4. **Network Policies**: Kubernetes network isolation
5. **Backup/Restore**: Configuration backup and rollback
6. **Validation**: Comprehensive configuration validation

## Supported Providers

- **OpenAI**: GPT-4, GPT-3.5 models
- **Anthropic**: Claude 3.5, Claude 3 models
- **Azure OpenAI**: Azure-hosted OpenAI models
- **Hugging Face**: Open source models
- **Google Vertex AI**: Google Cloud models
- **Mistral AI**: Mistral models
- **Cohere**: Cohere language models
- **Ollama**: Local models

## Testing

Run the comprehensive test suite:

```bash
cd monitoring
python test_dynamic_providers.py
```

Tests cover:
- Provider registration and management
- Configuration resolution
- NeMo Guardrails integration  
- Configuration migration
- Error handling and validation

## Benefits

1. **Security**: No hardcoded API keys in configuration files
2. **Flexibility**: Runtime provider configuration changes
3. **Multi-tenant**: Different API keys per deployment/user
4. **Scalability**: Centralized provider management
5. **Maintainability**: Clean separation of concerns
6. **Migration**: Easy transition from legacy configurations

## Environment Variables

Key environment variables for deployment:

```bash
# Core settings
NODE_ENV=production
ENABLE_DYNAMIC_PROVIDERS=true
PROVIDER_CONFIG_PATH=/app/config/dynamic-providers

# API keys (legacy support)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
AZURE_OPENAI_API_KEY=your-azure-key

# CORS configuration
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CORS_ALLOW_CREDENTIALS=false

# Redis for session storage
REDIS_PASSWORD=secure-redis-password
```

This system transforms NeMo Guardrails from a static configuration system to a dynamic, API-driven platform that can adapt to any LLM provider configuration at runtime while maintaining security and reliability.