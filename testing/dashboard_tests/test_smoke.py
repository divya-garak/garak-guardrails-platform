#!/usr/bin/env python3
"""
Smoke tests to verify pytest structure and basic functionality
These tests don't require external services and should always pass
"""

import pytest
from typing import List, Dict


class TestPytestStructure:
    """Smoke tests for pytest structure."""
    
    def test_imports_work(self):
        """Test that all required imports work."""
        import requests
        import json
        import time
        assert True
    
    def test_fixtures_available(self, service_urls: Dict[str, str], api_timeout: int):
        """Test that fixtures from conftest.py are available."""
        assert isinstance(service_urls, dict)
        assert "main" in service_urls
        assert isinstance(api_timeout, int)
        assert api_timeout > 0
    
    @pytest.mark.parametrize("test_input,expected", [
        ("hello", str),
        (123, int),
        (["a", "b"], list)
    ])
    def test_parametrize_works(self, test_input, expected):
        """Test that parametrized tests work correctly."""
        assert isinstance(test_input, expected)
    
    def test_markers_configured(self, pytestconfig):
        """Test that custom markers are properly configured."""
        markers = pytestconfig.getini("markers")
        markers_str = str(markers)
        expected_markers = ["integration", "docker", "slow"]
        for marker in expected_markers:
            assert marker in markers_str, f"Marker '{marker}' should be configured"
    
    def test_test_data_structure(self):
        """Test that test data structures are properly defined."""
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from test_guardrails import TEST_CASES
        
        assert isinstance(TEST_CASES, dict)
        expected_categories = ["jailbreak_detection", "sensitive_data", "content_safety", "safe_requests"]
        
        for category in expected_categories:
            assert category in TEST_CASES, f"Category '{category}' should be in TEST_CASES"
            assert isinstance(TEST_CASES[category], list), f"Category '{category}' should be a list"
            assert len(TEST_CASES[category]) > 0, f"Category '{category}' should not be empty"


def test_legacy_compatibility():
    """Test that legacy main functions exist for backward compatibility."""
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    
    from test_comprehensive import main as comp_main
    from test_docker_integration import main as docker_main
    from test_guardrails import main as guardrails_main
    
    # Just check that the functions exist and are callable
    assert callable(comp_main)
    assert callable(docker_main)
    assert callable(guardrails_main)


def test_directory_structure():
    """Test that the dashboard_tests directory has the expected structure."""
    import os
    
    current_dir = os.path.dirname(__file__)
    expected_files = [
        "__init__.py",
        "conftest.py", 
        "pytest.ini",
        "README.md",
        "test_comprehensive.py",
        "test_docker_integration.py", 
        "test_guardrails.py"
    ]
    
    for filename in expected_files:
        filepath = os.path.join(current_dir, filename)
        assert os.path.exists(filepath), f"Expected file '{filename}' should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])