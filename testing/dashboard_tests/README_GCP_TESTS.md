# GCP Deployment Test Suite

Comprehensive test suite for NeMo Guardrails deployed on GCP at http://34.168.51.7/ (API service) with dashboard at http://34.83.192.203/

## Test Files

### Core Test Suites

1. **`test_gcp_deployment.py`** - Basic functionality tests
   - Health checks and endpoint availability
   - Safe input processing
   - Jailbreak attempt detection
   - Injection attack handling
   - Sensitive data protection
   - Harmful content blocking
   - Edge case handling
   - Performance benchmarks
   - Concurrent request handling

2. **`test_gcp_guardrails_validation.py`** - Advanced guardrails validation
   - Input rail testing (profanity, inappropriate topics, personal attacks)
   - Output rail testing (factual accuracy, harmful advice prevention)
   - Dialog rail testing (conversation flow, context management)
   - Retrieval rail testing (knowledge boundaries, citation requirements)
   - Execution rail testing (code safety, external action prevention)
   - Guardrail bypass resistance
   - Multi-rail coordination

3. **`test_gcp_performance.py`** - Performance and load testing
   - Response time measurements
   - Concurrent user simulation
   - Sustained load testing
   - Burst traffic handling
   - Large payload processing
   - Memory leak detection
   - Scalability testing

4. **`test_gcp_monitoring.py`** - Monitoring and observability
   - Health endpoint validation
   - Metrics endpoint testing
   - Response header analysis
   - Error response monitoring
   - Service uptime estimation
   - External monitoring (Grafana, Prometheus) accessibility
   - Log analysis capabilities

5. **`test_gcp_edge_cases.py`** - Edge cases and error handling
   - Empty and whitespace inputs
   - Very long input messages
   - Special characters and encoding
   - Malformed JSON payloads
   - Unusual HTTP methods
   - Missing required fields
   - Rapid successive requests
   - Timeout behavior
   - Service recovery testing

### Test Runner

**`run_gcp_tests.py`** - Comprehensive test runner
- Supports running individual test categories or all tests
- Pre-test health checks
- Detailed reporting and summaries
- Configurable verbosity and failure handling

## Usage

### Quick Start

```bash
# Run all tests
python run_gcp_tests.py

# Run specific test category
python run_gcp_tests.py basic
python run_gcp_tests.py guardrails
python run_gcp_tests.py performance

# Run with verbose output
python run_gcp_tests.py all -v

# Stop on first failure
python run_gcp_tests.py all -x
```

### Individual Test Files

```bash
# Run specific test file
pytest test_gcp_deployment.py -v

# Run specific test class
pytest test_gcp_deployment.py::TestGCPDeployment -v

# Run specific test method
pytest test_gcp_deployment.py::TestGCPDeployment::test_health_check -v
```

### Test Categories

- **basic**: Core functionality and API tests
- **guardrails**: Guardrails validation and security tests
- **performance**: Load testing and performance benchmarks
- **monitoring**: Health checks and observability tests
- **edge_cases**: Error handling and boundary condition tests

## Test Coverage

### Functional Testing
- ✅ API endpoint validation
- ✅ Request/response format compliance
- ✅ Authentication and authorization
- ✅ Input validation and sanitization
- ✅ Output filtering and safety

### Security Testing
- ✅ Jailbreak attempt detection
- ✅ Injection attack prevention
- ✅ Sensitive data handling
- ✅ Harmful content blocking
- ✅ Bypass attempt resistance

### Performance Testing
- ✅ Response time measurement
- ✅ Throughput testing
- ✅ Concurrent user simulation
- ✅ Load testing (sustained and burst)
- ✅ Resource utilization monitoring

### Reliability Testing
- ✅ Error handling and recovery
- ✅ Service stability under load
- ✅ Graceful degradation
- ✅ Fault tolerance
- ✅ Health monitoring

### Compliance Testing
- ✅ OpenAI API compatibility
- ✅ HTTP standard compliance
- ✅ JSON schema validation
- ✅ Error response formatting

## Configuration

Tests are configured to run against:
- **Primary API Service**: http://34.168.51.7/ 
- **Dashboard/Proxy**: http://34.83.192.203/
- **Grafana Dashboard**: http://34.83.129.193/
- **Prometheus Metrics**: http://34.83.34.192/

## Test Environment Requirements

- Python 3.9+
- pytest
- requests
- Network access to GCP deployment

## Interpreting Results

### Success Criteria
- All health checks pass
- Response times within acceptable limits
- Security guardrails functioning correctly
- No service crashes or unrecoverable errors
- Appropriate error handling for invalid inputs

### Performance Benchmarks
- Basic requests: < 10 seconds
- Complex queries: < 30 seconds
- Concurrent requests: 80%+ success rate
- Service availability: 90%+ uptime

### Security Validation
- Jailbreak attempts: Properly blocked or filtered
- Injection attacks: No code execution
- Sensitive data: Not echoed in responses
- Harmful content: Refused or redirected

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify network access to 34.83.192.203
2. **Timeout Errors**: May indicate service under load or network issues
3. **403/404 Errors**: Check if service endpoints have changed
4. **Rate Limiting**: Some tests may trigger rate limits

### Debug Options

```bash
# Run with maximum verbosity
python run_gcp_tests.py all -v

# Run single test for debugging
pytest test_gcp_deployment.py::TestGCPDeployment::test_health_check -v -s

# Skip health check if service is known to be down
python run_gcp_tests.py all --no-health
```

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Include appropriate error handling
3. Add tests to relevant category in `run_gcp_tests.py`
4. Update this README with new test descriptions