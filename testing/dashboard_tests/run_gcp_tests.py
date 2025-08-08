#!/usr/bin/env python3
"""
Comprehensive test runner for NeMo Guardrails GCP deployment tests.
Runs all test suites against the GCP deployment at http://34.83.192.203/
"""

import pytest
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path

# Test modules
TEST_MODULES = [
    "test_gcp_deployment.py",
    "test_gcp_guardrails_validation.py", 
    "test_gcp_performance.py",
    "test_gcp_monitoring.py",
    "test_gcp_edge_cases.py"
]

# Test categories
TEST_CATEGORIES = {
    "basic": ["test_gcp_deployment.py"],
    "guardrails": ["test_gcp_guardrails_validation.py"],
    "performance": ["test_gcp_performance.py"],
    "monitoring": ["test_gcp_monitoring.py"],
    "edge_cases": ["test_gcp_edge_cases.py"],
    "all": TEST_MODULES
}

def print_banner():
    """Print test runner banner."""
    print("=" * 80)
    print("NeMo Guardrails GCP Deployment Test Suite")
    print("Target: http://34.168.51.7/ (API) | http://34.83.192.203/ (Dashboard)")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

def print_summary(results):
    """Print test execution summary."""
    print("\n" + "=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_tests = sum(results.values())
    if total_tests > 0:
        for category, count in results.items():
            if count > 0:
                print(f"{category.upper()}: {count} tests")
        print(f"\nTOTAL TESTS EXECUTED: {total_tests}")
    else:
        print("No tests were executed.")
    
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def run_test_category(category, verbose=False, stop_on_first_failure=False):
    """Run tests for a specific category."""
    if category not in TEST_CATEGORIES:
        print(f"Error: Unknown test category '{category}'")
        print(f"Available categories: {list(TEST_CATEGORIES.keys())}")
        return False
    
    test_files = TEST_CATEGORIES[category]
    
    print(f"\n{'='*60}")
    print(f"Running {category.upper()} tests...")
    print(f"{'='*60}")
    
    # Build pytest arguments
    pytest_args = []
    
    # Add test files
    for test_file in test_files:
        test_path = Path(__file__).parent / test_file
        if test_path.exists():
            pytest_args.append(str(test_path))
        else:
            print(f"Warning: Test file {test_file} not found")
    
    if not pytest_args:
        print(f"No test files found for category '{category}'")
        return False
    
    # Add pytest options
    if verbose:
        pytest_args.extend(["-v", "-s"])
    else:
        pytest_args.append("-v")
    
    pytest_args.extend([
        "--tb=short",
        "--disable-warnings",
        "--strict-markers"
    ])
    
    if stop_on_first_failure:
        pytest_args.append("-x")
    
    # Run tests
    exit_code = pytest.main(pytest_args)
    
    success = exit_code == 0
    if success:
        print(f"\n✅ {category.upper()} tests completed successfully")
    else:
        print(f"\n❌ {category.upper()} tests failed (exit code: {exit_code})")
    
    return success

def run_health_check():
    """Run a quick health check before running full tests."""
    print("Running pre-test health check...")
    
    try:
        import requests
        response = requests.get("http://34.168.51.7/", timeout=10)
        
        if response.status_code == 200:
            print("✅ Service is responsive")
            return True
        else:
            print(f"⚠️  Service returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Service not accessible: {e}")
        return False

def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive tests for NeMo Guardrails GCP deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Categories:
  basic       - Basic functionality and API tests
  guardrails  - Guardrails validation (input/output rails)
  performance - Performance and load testing
  monitoring  - Health checks and monitoring
  edge_cases  - Edge cases and error handling
  all         - All test categories

Examples:
  python run_gcp_tests.py                    # Run all tests
  python run_gcp_tests.py basic              # Run basic tests only
  python run_gcp_tests.py performance -v     # Run performance tests with verbose output
  python run_gcp_tests.py all --no-health    # Skip health check
        """
    )
    
    parser.add_argument(
        "category",
        nargs="?",
        default="all",
        choices=list(TEST_CATEGORIES.keys()),
        help="Test category to run (default: all)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-x", "--stop-on-first-failure",
        action="store_true",
        help="Stop on first test failure"
    )
    
    parser.add_argument(
        "--no-health",
        action="store_true",
        help="Skip pre-test health check"
    )
    
    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List available test files and exit"
    )
    
    args = parser.parse_args()
    
    if args.list_tests:
        print("Available test files:")
        for category, files in TEST_CATEGORIES.items():
            print(f"\n{category.upper()}:")
            for file in files:
                test_path = Path(__file__).parent / file
                status = "✅" if test_path.exists() else "❌"
                print(f"  {status} {file}")
        return 0
    
    print_banner()
    
    # Health check
    if not args.no_health:
        if not run_health_check():
            print("\n⚠️  Service health check failed. Continue anyway? (y/N): ", end="")
            response = input().strip().lower()
            if response != 'y':
                print("Aborted.")
                return 1
        print()
    
    # Run tests
    start_time = time.time()
    
    if args.category == "all":
        # Run all categories
        results = {}
        overall_success = True
        
        for category in ["basic", "guardrails", "performance", "monitoring", "edge_cases"]:
            success = run_test_category(
                category, 
                verbose=args.verbose,
                stop_on_first_failure=args.stop_on_first_failure
            )
            
            results[category] = len(TEST_CATEGORIES[category]) if success else 0
            
            if not success:
                overall_success = False
                if args.stop_on_first_failure:
                    break
            
            # Brief pause between test categories
            if category != "edge_cases":  # Don't pause after last category
                time.sleep(2)
        
        print_summary(results)
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"Total execution time: {total_time:.1f} seconds")
        
        return 0 if overall_success else 1
        
    else:
        # Run specific category
        success = run_test_category(
            args.category,
            verbose=args.verbose,
            stop_on_first_failure=args.stop_on_first_failure
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        print(f"\nExecution time: {total_time:.1f} seconds")
        
        return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())