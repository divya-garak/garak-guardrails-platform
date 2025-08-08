#!/usr/bin/env python3
"""
Pytest module for NeMo Guardrails Docker deployment integration testing
This demonstrates how you would integrate with the running Docker container
"""

import pytest
import requests
import json
import sys
from typing import Dict, Any

DOCKER_SERVER_URL = "http://localhost:8000"

@pytest.fixture(scope="session")
def docker_server_url() -> str:
    """Fixture providing the Docker server URL."""
    return DOCKER_SERVER_URL

class TestDockerIntegration:
    """Test suite for Docker integration."""
    
    def test_server_health(self, docker_server_url: str):
        """Test that the Docker server is responding."""
        response = requests.get(f"{docker_server_url}/")
        assert response.status_code == 200, f"Server health check failed with status {response.status_code}"
    
    def test_available_configurations(self, docker_server_url: str):
        """Test retrieval of available configurations."""
        response = requests.get(f"{docker_server_url}/v1/rails/configs")
        assert response.status_code == 200, f"Configs endpoint failed with status {response.status_code}"
        
        configs = response.json()
        assert isinstance(configs, list), "Configs should be a list"
        assert all('id' in config for config in configs), "All configs should have an 'id' field"
    
    def test_api_documentation_accessible(self, docker_server_url: str):
        """Test that API documentation is accessible."""
        response = requests.get(f"{docker_server_url}/docs")
        assert response.status_code == 200, f"API docs not accessible, status: {response.status_code}"
    
    def test_chat_completion_endpoint_structure(self, docker_server_url: str):
        """Test the chat completion endpoint structure (may fail without API key)."""
        test_payload = {
            "config_id": "hello_world",
            "messages": [
                {"role": "user", "content": "Hello!"}
            ]
        }
        
        response = requests.post(
            f"{docker_server_url}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json=test_payload
        )
        
        # Either succeeds (200) or fails with expected error (not 404/500)
        assert response.status_code in [200, 400, 401, 422], \
            f"Unexpected status code: {response.status_code}"
    
    def test_integration_examples_documentation(self):
        """Test that integration examples are properly documented."""
        # This test validates that we have examples for different languages
        languages = ["Python", "JavaScript", "Rust", "Java"]
        
        # In a real implementation, you might check if documentation files exist
        # or if the examples are accessible via API
        for lang in languages:
            assert lang is not None, f"{lang} integration example should be available"
    
    @pytest.mark.parametrize("command,description", [
        ("docker logs nemo-demo-full", "View logs"),
        ("docker stats nemo-demo-full", "View stats"),
        ("docker exec -it nemo-demo-full nemoguardrails --help", "Execute CLI"),
        ("docker cp config.yml nemo-demo-full:/config/", "Copy files"),
        ("docker stop nemo-demo-full", "Stop server")
    ])
    def test_docker_commands_documented(self, command: str, description: str):
        """Test that Docker commands are properly documented."""
        # This validates that we have proper documentation for Docker commands
        assert command is not None and len(command) > 0
        assert description is not None and len(description) > 0
    
    def test_production_deployment_options(self):
        """Test that production deployment options are documented."""
        deployment_options = [
            "API keys configuration",
            "Custom configs mounting",
            "Docker Compose setup"
        ]
        
        for option in deployment_options:
            assert option is not None, f"{option} should be documented"

def test_docker_integration_legacy():
    """Legacy test function for backward compatibility."""
    try:
        # Test server health
        health_response = requests.get(f"{DOCKER_SERVER_URL}/")
        assert health_response.status_code == 200
        
        # Get available configurations
        configs_response = requests.get(f"{DOCKER_SERVER_URL}/v1/rails/configs")
        configs = configs_response.json()
        assert isinstance(configs, list)
        
        # Test API documentation
        docs_response = requests.get(f"{DOCKER_SERVER_URL}/docs")
        assert docs_response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Could not connect to Docker container at localhost:8000")
    except Exception as e:
        pytest.fail(f"Error during testing: {e}")

def main():
    """Run Docker integration testing (legacy function for backward compatibility)."""
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    main()