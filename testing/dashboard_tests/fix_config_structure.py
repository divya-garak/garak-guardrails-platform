#!/usr/bin/env python3
"""
Quick fix to test the configuration without recreating the entire deployment.
This script will test if we can use the configuration that's currently mounted.
"""

import requests
import json

ENDPOINT = "http://35.197.35.26:8000"

def test_without_config_id():
    """Test with no config_id to see if server has a default"""
    print("Testing without config_id...")
    
    payload = {
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    response = requests.post(
        f"{ENDPOINT}/v1/chat/completions",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    return response.status_code == 200

def test_available_configs():
    """Try to determine what configs are available"""
    print("Checking available configurations...")
    
    # Try to get OpenAPI spec to see available configs
    try:
        response = requests.get(f"{ENDPOINT}/openapi.json", timeout=30)
        if response.status_code == 200:
            spec = response.json()
            # Look for config_id schema or examples
            print("OpenAPI spec retrieved - checking for config information...")
            # This would require parsing the complex OpenAPI spec
        
    except Exception as e:
        print(f"Error getting OpenAPI spec: {e}")

    # Try some common config names that might work with the current setup
    possible_configs = [
        "",  # Empty string
        "config",  # Base filename 
        "simple_security",  # From our configmap name
    ]
    
    for config_name in possible_configs:
        print(f"\nTesting config: '{config_name}'")
        payload = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        if config_name:
            payload["config_id"] = config_name
            
        response = requests.post(
            f"{ENDPOINT}/v1/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

def main():
    print("🔧 NeMo Guardrails Configuration Diagnostics")
    print("=" * 50)
    
    # Test basic connectivity
    try:
        response = requests.get(f"{ENDPOINT}/", timeout=10)
        print(f"Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection failed: {e}")
        return
    
    # Test configurations
    test_without_config_id()
    print()
    test_available_configs()

if __name__ == "__main__":
    main()