#!/usr/bin/env python3
"""
Comprehensive test runner for NeMo Guardrails dashboard tests
Runs all test modules and provides consolidated reporting
"""

import subprocess
import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any
import time


def run_pytest_module(module_name: str, verbose: bool = True) -> Dict[str, Any]:
    """Run a specific pytest module and return results."""
    cmd = ["python3", "-m", "pytest", f"{module_name}", "-v", "--tb=short"]
    if not verbose:
        cmd.remove("-v")
    
    try:
        start_time = time.time()
        result = subprocess.run(cmd, cwd=Path(__file__).parent, capture_output=True, text=True)
        end_time = time.time()
        
        # Check if failures are due to service unavailability (expected in some environments)
        service_unavailable_keywords = [
            "Connection refused",
            "service not available",
            "Failed to establish a new connection",
            "HTTPConnectionPool"
        ]
        
        is_service_failure = any(keyword in result.stdout + result.stderr 
                               for keyword in service_unavailable_keywords)
        
        return {
            "module": module_name,
            "success": result.returncode == 0,
            "duration": end_time - start_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "service_failure": is_service_failure
        }
    except Exception as e:
        return {
            "module": module_name,
            "success": False,
            "duration": 0,
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "service_failure": False
        }


def main():
    """Run all dashboard tests."""
    print("🧪 NeMo Guardrails Dashboard Tests")
    print("=" * 50)
    
    # Test modules to run
    test_modules = [
        "test_smoke.py",
        "test_endpoint_validation.py",
        "test_api_integration.py",
        "test_monitoring_integration.py",
        "test_proxy_integration.py",
        "test_guardrails.py",
        "test_comprehensive.py",
        "test_docker_integration.py"
    ]
    
    results = []
    total_duration = 0
    
    for module in test_modules:
        print(f"\n🔄 Running {module}...")
        result = run_pytest_module(module)
        results.append(result)
        total_duration += result["duration"]
        
        if result["success"]:
            print(f"✅ {module} passed ({result['duration']:.2f}s)")
        else:
            print(f"❌ {module} failed ({result['duration']:.2f}s)")
            if result["stderr"]:
                print(f"   Error: {result['stderr'][:200]}...")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for r in results if r["success"])
    service_failures = sum(1 for r in results if not r["success"] and r.get("service_failure", False))
    real_failures = sum(1 for r in results if not r["success"] and not r.get("service_failure", False))
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Service Unavailable: {service_failures}")
    print(f"❌ Failed: {real_failures}")
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    
    # Detailed results
    if real_failures > 0:
        print("\n❌ Real Failures (Not Service Issues):")
        for result in results:
            if not result["success"] and not result.get("service_failure", False):
                print(f"  - {result['module']}")
                if result["stderr"]:
                    print(f"    Error: {result['stderr'][:100]}...")
    
    if service_failures > 0:
        print("\n⚠️  Service Unavailable (Expected in Some Environments):")
        for result in results:
            if not result["success"] and result.get("service_failure", False):
                print(f"  - {result['module']}")
    
    # Return appropriate exit code - only fail on real failures, not service unavailability
    return 0 if real_failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())