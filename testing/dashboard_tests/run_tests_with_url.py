#!/usr/bin/env python3
"""
Test runner script that allows setting custom URL for NeMo Guardrails tests
Usage: python run_tests_with_url.py [URL] [test_file]
"""

import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_tests_with_url.py [URL] [optional: test_file]")
        print("Example: python run_tests_with_url.py http://localhost:8050")
        print("Example: python run_tests_with_url.py http://localhost:8050 test_comprehensive.py")
        return
    
    url = sys.argv[1]
    
    # Ensure URL has the full chat completions endpoint
    if not url.endswith('/v1/chat/completions'):
        if url.endswith('/'):
            url = url[:-1]
        url = url + '/v1/chat/completions'
    
    # Set environment variable
    os.environ['NEMO_TEST_URL'] = url
    
    print(f"🚀 Running tests against: {url}")
    print("=" * 60)
    
    # Determine which tests to run
    if len(sys.argv) >= 3:
        test_file = sys.argv[2]
        cmd = ["python3", "-m", "pytest", test_file, "-v"]
    else:
        # Run main test suites
        test_files = [
            "test_api_integration.py",
            "test_comprehensive.py", 
            "test_endpoint_validation.py"
        ]
        cmd = ["python3", "-m", "pytest"] + test_files + ["-v"]
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)