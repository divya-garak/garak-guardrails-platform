#!/usr/bin/env python3
"""
Local Test Runner for NeMo Guardrails Dashboard Tests
This script can run tests against locally running services or mock services
"""

import argparse
import os
import sys
import time
import requests
import subprocess
from typing import Dict, List, Optional
from unittest.mock import patch, MagicMock


# Service endpoints
SERVICES = {
    "main": "http://localhost:8000",
    "comprehensive": "http://localhost:8004", 
    "jailbreak": "http://localhost:1337",
    "presidio": "http://localhost:5001",
    "content_safety": "http://localhost:5002",
    "llama_guard": "http://localhost:8001",
    "factcheck": "http://localhost:5000"
}


class Colors:
    """Terminal colors for pretty output."""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_status(message: str, color: str = Colors.GREEN):
    """Print a colored status message."""
    print(f"{color}[INFO]{Colors.NC} {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")


def check_service_health(service_name: str, url: str, timeout: int = 5) -> bool:
    """Check if a service is healthy."""
    try:
        endpoints_to_try = [
            f"{url}/health",
            f"{url}/",
            f"{url}/docs"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(endpoint, timeout=timeout)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                continue
        
        return False
    except Exception:
        return False


def get_service_status() -> Dict[str, bool]:
    """Get the health status of all services."""
    print_status("Checking service health...")
    status = {}
    
    for service_name, url in SERVICES.items():
        is_healthy = check_service_health(service_name, url)
        status[service_name] = is_healthy
        
        if is_healthy:
            print_status(f"✓ {service_name} ({url})")
        else:
            print_warning(f"✗ {service_name} ({url}) - not available")
    
    healthy_count = sum(status.values())
    total_count = len(status)
    
    print_status(f"Services available: {healthy_count}/{total_count}")
    return status


def create_mock_responses():
    """Create mock responses for unavailable services."""
    
    def mock_jailbreak_response(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "is_jailbreak": True,
            "confidence": 0.8,
            "reason": "Mock jailbreak detection"
        }
        return mock_response
    
    def mock_presidio_response(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "has_sensitive_data": True,
            "entities": [{"type": "PHONE_NUMBER", "start": 0, "end": 12}],
            "anonymized_text": "[PHONE_NUMBER] detected"
        }
        return mock_response
    
    def mock_content_safety_response(*args, **kwargs):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "is_safe": False,
            "categories_violated": ["hate_speech"],
            "confidence": 0.9
        }
        return mock_response
    
    def mock_main_guardrails_response(*args, **kwargs):
        url = args[0] if args else kwargs.get('url', '')
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        if 'chat/completions' in url:
            mock_response.json.return_value = {
                "choices": [{
                    "message": {
                        "content": "I can't help with that request as it violates our guidelines."
                    }
                }]
            }
        elif 'rails/configs' in url:
            mock_response.json.return_value = [
                {"id": "hello_world", "name": "Hello World Config"},
                {"id": "balanced", "name": "Balanced Config"}
            ]
        else:
            mock_response.json.return_value = {"status": "ok", "message": "Mock service"}
        
        return mock_response
    
    return {
        "jailbreak": mock_jailbreak_response,
        "presidio": mock_presidio_response,
        "content_safety": mock_content_safety_response,
        "main": mock_main_guardrails_response,
        "comprehensive": mock_main_guardrails_response
    }


def run_tests_with_mocks(service_status: Dict[str, bool], pytest_args: List[str]) -> int:
    """Run tests with mocked services for unavailable ones."""
    mock_responses = create_mock_responses()
    unavailable_services = [name for name, healthy in service_status.items() if not healthy]
    
    if unavailable_services:
        print_status(f"Mocking unavailable services: {', '.join(unavailable_services)}")
    
    # Create patches for unavailable services
    patches = []
    
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        
        def smart_post(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            
            # Check which service this request is for
            for service_name, service_url in SERVICES.items():
                if service_url in url and not service_status.get(service_name, False):
                    if service_name in mock_responses:
                        return mock_responses[service_name](*args, **kwargs)
            
            # If service is available, make real request
            return requests.post(*args, **kwargs)
        
        def smart_get(*args, **kwargs):
            url = args[0] if args else kwargs.get('url', '')
            
            # Check which service this request is for  
            for service_name, service_url in SERVICES.items():
                if service_url in url and not service_status.get(service_name, False):
                    if service_name in mock_responses:
                        return mock_responses[service_name](*args, **kwargs)
            
            # If service is available, make real request
            return requests.get(*args, **kwargs)
        
        mock_post.side_effect = smart_post
        mock_get.side_effect = smart_get
        
        # Run pytest
        cmd = ["python3", "-m", "pytest"] + pytest_args
        print_status(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return result.returncode


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Local test runner for NeMo Guardrails dashboard tests"
    )
    parser.add_argument(
        "--mock-unavailable", 
        action="store_true",
        help="Mock responses for unavailable services"
    )
    parser.add_argument(
        "--check-only",
        action="store_true", 
        help="Only check service status and exit"
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Arguments to pass to pytest"
    )
    
    args = parser.parse_args()
    
    print_status("🧪 NeMo Guardrails Local Test Runner")
    print_status("=" * 50)
    
    # Check service status
    service_status = get_service_status()
    
    if args.check_only:
        return 0
    
    # Default pytest arguments
    pytest_args = args.pytest_args if args.pytest_args else ["-v", "--tb=short"]
    
    # Run tests
    if args.mock_unavailable:
        return run_tests_with_mocks(service_status, pytest_args)
    else:
        # Run tests normally
        cmd = ["python3", "-m", "pytest"] + pytest_args
        print_status(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return result.returncode


if __name__ == "__main__":
    sys.exit(main())