# Dashboard Tests

This directory contains pytest-based tests for the NeMo Guardrails dashboard and related services.

## Test Structure

- `test_comprehensive.py` - Comprehensive guardrails configuration tests
- `test_docker_integration.py` - Docker deployment integration tests  
- `test_guardrails.py` - Individual guardrail service tests
- `test_smoke.py` - Smoke tests for pytest structure validation
- `conftest.py` - Shared pytest fixtures and configuration
- `pytest.ini` - Pytest configuration

## How to Test

### Quick Start (Recommended)

**Option 1: Full Integration Testing**
```bash
# Navigate to dashboard_tests directory
cd dashboard_tests/

# Run all tests with Docker services (handles everything automatically)
./run_full_tests.sh
```

**Option 2: Local Development Testing**
```bash
# Check what services are currently running
./run_local_tests.py --check-only

# Run tests with automatic mocking for unavailable services
./run_local_tests.py --mock-unavailable
```

### Detailed Testing Options

#### 1. Full Integration Testing (Docker-based)

The `run_full_tests.sh` script provides complete service lifecycle management:

```bash
# Basic usage - runs all tests
./run_full_tests.sh

# Run specific test file
./run_full_tests.sh test_comprehensive.py

# Run tests matching a pattern
./run_full_tests.sh -k "docker"
./run_full_tests.sh -k "integration"

# Run with verbose output
./run_full_tests.sh -v

# Show service logs if tests fail
./run_full_tests.sh --logs-only

# Cleanup services without running tests
./run_full_tests.sh --cleanup-only

# Skip initial cleanup (if services already running)
./run_full_tests.sh --skip-cleanup

# Show all options
./run_full_tests.sh --help
```

**What it does:**
- Stops and cleans up any existing services
- Builds and starts all required Docker services
- Waits for services to be healthy
- Runs the specified tests
- Shows service logs if tests fail
- Cleans up services after testing

#### 2. Local Development Testing

The `run_local_tests.py` script is designed for development workflows:

```bash
# Check which services are running
./run_local_tests.py --check-only

# Run with mocking for unavailable services
./run_local_tests.py --mock-unavailable

# Run specific test files
./run_local_tests.py test_smoke.py
./run_local_tests.py test_docker_integration.py

# Pass pytest arguments
./run_local_tests.py test_comprehensive.py --tb=short
```

**Mock Testing Features:**
- Automatically detects which services are unavailable
- Provides realistic mock responses for testing
- Allows development without running heavy Docker services
- Maintains test coverage even when services are down

#### 3. Manual Testing (Advanced)

For direct pytest usage (requires services to be manually started):

```bash
# All tests
pytest -v

# Specific test file
pytest test_comprehensive.py -v

# Using markers
pytest -m integration          # Integration tests only
pytest -m docker              # Docker-related tests only  
pytest -m "not slow"          # Skip slow tests
pytest -m "integration and not slow"  # Combined markers

# Pattern matching
pytest -k "docker"            # Tests with "docker" in name
pytest -k "test_health"       # Health check tests
pytest -k "not batch"         # Exclude batch tests

# Detailed output options
pytest --tb=short             # Short traceback format
pytest --tb=line              # One line per failure
pytest --maxfail=3            # Stop after 3 failures
pytest --lf                   # Run last failed tests only
pytest --ff                   # Run failures first

# Coverage reporting (if pytest-cov installed)
pytest --cov=. --cov-report=html
```

### Test Categories and Examples

#### Smoke Tests (Always Pass)
```bash
# Quick validation that pytest structure works
pytest test_smoke.py -v
./run_local_tests.py test_smoke.py
```

#### Docker Integration Tests
```bash
# Test Docker service integration
pytest test_docker_integration.py -v
./run_full_tests.sh test_docker_integration.py
```

#### Comprehensive Guardrails Tests
```bash
# Test all guardrail functionality (requires services)
./run_full_tests.sh test_comprehensive.py
./run_local_tests.py --mock-unavailable test_comprehensive.py
```

#### Individual Service Tests
```bash
# Test specific guardrail services
./run_full_tests.sh test_guardrails.py
pytest -m "not slow" test_guardrails.py  # Skip batch tests
```

### Troubleshooting Tests

#### Common Issues

**1. Services Not Available**
```bash
# Check service status
./run_local_tests.py --check-only

# Use mocking for development
./run_local_tests.py --mock-unavailable

# Full Docker restart
./run_full_tests.sh --cleanup-only
./run_full_tests.sh
```

**2. Docker Issues**
```bash
# Check Docker status
docker --version
docker-compose --version
docker info

# Clean Docker state
docker system prune -f
./run_full_tests.sh --cleanup-only
```

**3. Port Conflicts**
```bash
# Check what's using test ports
lsof -i :8000 -i :8001 -i :8004 -i :1337 -i :5000 -i :5001 -i :5002

# Kill conflicting processes
./run_full_tests.sh --cleanup-only
```

**4. API Key Issues**
```bash
# Check environment configuration
cat .env

# Copy template and configure
cp .env.template .env
# Edit .env with your API keys
```

#### Debug Mode

**View Service Logs:**
```bash
# Show logs for all services
./run_full_tests.sh --logs-only

# Show logs for specific service
docker-compose -f docker-compose.test.yml logs jailbreak-service

# Follow logs in real-time
docker-compose -f docker-compose.test.yml logs -f content-safety
```

**Verbose Testing:**
```bash
# Maximum verbosity
./run_full_tests.sh -v --tb=long

# Pytest debugging
pytest --pdb                  # Drop into debugger on failure
pytest -s                     # Don't capture output
pytest --lf -v                # Rerun last failed with verbose
```

### Performance Optimization

**Fast Testing Strategies:**
```bash
# Run only smoke tests for quick validation
pytest test_smoke.py

# Skip slow tests during development
pytest -m "not slow"

# Run specific test patterns
pytest -k "health" -v

# Use mocking for faster iteration
./run_local_tests.py --mock-unavailable -k "integration"
```

**Resource Management:**
```bash
# Cleanup between test runs
./run_full_tests.sh --cleanup-only

# Monitor resource usage
docker stats

# Limit Docker resources if needed
docker-compose -f docker-compose.test.yml up --scale llama-guard=0
```

## Test Categories

### Integration Tests
Tests that verify the integration between different services and components.

### Docker Tests
Tests that require Docker containers to be running. These tests will be skipped if Docker services are not available.

### Slow Tests
Tests that take longer to run, typically comprehensive test suites.

## Setup

1. **Copy environment template:**
   ```bash
   cp .env.template .env
   ```

2. **Configure API keys in `.env`:**
   ```bash
   OPENAI_API_KEY=your_actual_openai_api_key
   HUGGING_FACE_HUB_TOKEN=your_actual_hf_token
   # ... other keys as needed
   ```

3. **Ensure Docker is running:**
   ```bash
   docker --version
   docker-compose --version
   ```

## Prerequisites

Before running tests, ensure:

1. Docker and docker-compose are installed and running
2. Python 3.9+ with pytest installed
3. API keys configured in `.env` file (for full integration tests)
4. Sufficient system resources (8GB+ RAM recommended for all services)

## Service Endpoints

The tests expect the following services to be available:

- Main service: `http://localhost:8000`
- Jailbreak detection: `http://localhost:1337`
- Content safety: `http://localhost:5002`
- Presidio (sensitive data): `http://localhost:5001`
- Fact checking: `http://localhost:5000`
- LlamaGuard: `http://localhost:8001`

## Test Data

Test cases include:
- Legitimate prompts (should be allowed)
- Malicious prompts (should be blocked)
- Sensitive data samples
- Content safety violations
- Injection attempts

## Practical Examples

### Daily Development Workflow

```bash
# 1. Quick sanity check
./run_local_tests.py test_smoke.py

# 2. Test your changes with available services
./run_local_tests.py --mock-unavailable

# 3. Full integration test before commit
./run_full_tests.sh -v
```

### CI/CD Pipeline Integration

```bash
# In your CI script
cd dashboard_tests/
cp .env.template .env
# Set your CI environment variables
export OPENAI_API_KEY=$CI_OPENAI_KEY
export HUGGING_FACE_HUB_TOKEN=$CI_HF_TOKEN
./run_full_tests.sh --maxfail=1
```

### Debugging Failed Tests

```bash
# 1. Check which services are down
./run_local_tests.py --check-only

# 2. Run with maximum verbosity
./run_full_tests.sh -v --tb=long --maxfail=1

# 3. Check service logs
./run_full_tests.sh --logs-only

# 4. Run specific failing test
./run_full_tests.sh test_comprehensive.py -k "test_malicious_prompts"
```

### Performance Testing

```bash
# Fast iteration during development
./run_local_tests.py --mock-unavailable -m "not slow"

# Full performance test
./run_full_tests.sh --tb=short

# Specific service performance
./run_full_tests.sh test_guardrails.py -k "batch"
```

## Files Overview

- `run_full_tests.sh` - Complete Docker-based test runner
- `run_local_tests.py` - Development-friendly test runner with mocking
- `docker-compose.test.yml` - Service orchestration configuration
- `conftest.py` - Shared pytest fixtures and configuration
- `pytest.ini` - Test runner configuration
- `.env.template` - Environment variables template
- Test files: `test_*.py` - Individual test suites