"""
Shared pytest configuration and fixtures for dashboard tests.
"""

import pytest
import requests
import time
from typing import Dict, Any, Generator


@pytest.fixture(scope="session")
def wait_for_services():
    """Wait for all services to be ready before running tests."""
    print("⏳ Waiting for services to be ready...")
    time.sleep(5)
    yield
    print("✅ Test session completed")


@pytest.fixture(scope="session")
def api_timeout() -> int:
    """Default timeout for API requests."""
    return 30


@pytest.fixture(scope="session")
def service_urls() -> Dict[str, str]:
    """Service URLs used across tests."""
    return {
        "main": "http://localhost:8000",
        "docker": "http://localhost:8000",
        "comprehensive": "http://localhost:8004",
        "jailbreak": "http://localhost:1337",
        "factcheck": "http://localhost:5000",
        "llama_guard": "http://localhost:8001",
        "presidio": "http://localhost:5001",
        "content_safety": "http://localhost:5002",
        # External/deployment URLs
        "api_integration": "http://34.168.51.7",
        "proxy_integration": "http://34.83.192.203",
        "gcp_deployment": "http://34.83.192.203",
        "grafana": "http://34.83.129.193",
        "prometheus": "http://34.83.34.192"
    }


@pytest.fixture
def requests_session() -> Generator[requests.Session, None, None]:
    """Provide a requests session with default configuration."""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "User-Agent": "NeMo-Guardrails-Test/1.0"
    })
    yield session
    session.close()


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "docker: mark test as requiring Docker"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names."""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add docker marker to docker tests
        if "docker" in item.nodeid:
            item.add_marker(pytest.mark.docker)
        
        # Add slow marker to comprehensive tests
        if "comprehensive" in item.nodeid or "batch" in item.nodeid:
            item.add_marker(pytest.mark.slow)


@pytest.fixture(autouse=True)
def skip_if_service_unavailable(request):
    """Skip tests if required services are not available."""
    if hasattr(request.node, 'get_closest_marker'):
        docker_marker = request.node.get_closest_marker('docker')
        if docker_marker:
            try:
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code != 200:
                    pytest.skip("Docker service not available")
            except requests.exceptions.RequestException:
                pytest.skip("Docker service not available")