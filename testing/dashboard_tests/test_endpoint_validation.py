#!/usr/bin/env python3
"""
Pytest module for NeMo Guardrails endpoint validation tests
Tests various service endpoints and their availability
"""

import pytest
import requests
import json
import os
from typing import Dict, List, Any


class TestEndpointValidation:
    """Test suite for endpoint validation."""
    
    @pytest.fixture(scope="class")
    def nemo_url(self):
        """NeMo Guardrails URL fixture - configurable via environment variable."""
        return os.getenv("NEMO_TEST_URL", "http://34.168.51.7").replace("/v1/chat/completions", "")
    
    def test_root_endpoint(self, nemo_url: str):
        """Test root endpoint (Chat UI)."""
        try:
            response = requests.get(f"{nemo_url}/", timeout=10)
            # Chat UI should be accessible
            assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
            assert "NeMo Guardrails" in response.text or "chat" in response.text.lower(), "Expected chat UI content"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Root endpoint not accessible: {e}")
    
    def test_api_docs_endpoint(self, nemo_url: str):
        """Test API documentation endpoint."""
        try:
            response = requests.get(f"{nemo_url}/docs", timeout=10)
            # API docs should be accessible
            assert response.status_code == 200, f"API docs failed: {response.status_code}"
            assert any(keyword in response.text.lower() for keyword in ["api", "swagger", "openapi"]), "Expected API documentation content"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"API docs endpoint not accessible: {e}")
    
    def test_openapi_spec_endpoint(self, nemo_url: str):
        """Test OpenAPI specification endpoint."""
        try:
            response = requests.get(f"{nemo_url}/openapi.json", timeout=10)
            assert response.status_code == 200, f"OpenAPI spec failed: {response.status_code}"
            
            data = response.json()
            assert isinstance(data, dict), "OpenAPI spec should be a dictionary"
            assert "paths" in data, "OpenAPI spec should contain paths"
            
            endpoints = list(data.get('paths', {}).keys())
            assert len(endpoints) > 0, "Should have at least one API endpoint"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"OpenAPI spec endpoint not accessible: {e}")
    
    def test_rails_configs_endpoint(self, nemo_url: str):
        """Test rails configurations endpoint."""
        try:
            response = requests.get(f"{nemo_url}/v1/rails/configs", timeout=10)
            # Should respond with available configurations
            assert response.status_code == 200, f"Rails configs failed: {response.status_code}"
            
            data = response.json()
            assert isinstance(data, (list, dict)), "Rails configs should be a list or dictionary"
        except requests.exceptions.RequestException as e:
            pytest.skip(f"Rails configs endpoint not accessible: {e}")
    
    def test_health_endpoint_if_available(self, nemo_url: str):
        """Test health endpoint if available."""
        try:
            response = requests.get(f"{nemo_url}/health", timeout=5)
            if response.status_code == 200:
                # If health endpoint exists, it should return valid JSON
                data = response.json()
                assert isinstance(data, dict), "Health response should be a dictionary"
            else:
                pytest.skip("Health endpoint not available")
        except requests.exceptions.RequestException:
            pytest.skip("Health endpoint not accessible")
    
    @pytest.mark.parametrize("test_data", [
        ("test_hello.json", {"config_id": "config", "messages": [{"role": "user", "content": "Hello"}]}),
        ("test_dashboard.json", {"config_id": "config", "messages": [{"role": "user", "content": "Hello!"}]}),
    ])
    def test_json_test_data_format(self, test_data: tuple):
        """Test that JSON test data is valid."""
        test_name, expected_structure = test_data
        
        # Verify the test data structure is valid
        assert "config_id" in expected_structure, "Test data should have config_id"
        assert "messages" in expected_structure, "Test data should have messages"
        assert isinstance(expected_structure["messages"], list), "Messages should be a list"
        assert len(expected_structure["messages"]) > 0, "Should have at least one message"
        assert "role" in expected_structure["messages"][0], "Message should have role"
        assert "content" in expected_structure["messages"][0], "Message should have content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])