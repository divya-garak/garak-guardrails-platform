#!/usr/bin/env python3
"""
Edge cases and error handling tests for NeMo Guardrails GCP deployment at http://34.83.192.203/
Tests unusual inputs, boundary conditions, error scenarios, and recovery mechanisms.
"""

import pytest
import requests
import json
import time
import string
import random
from typing import Dict, List, Any, Optional

# GCP deployment base URL (actual API service)
GCP_BASE_URL = "https://api.garaksecurity.com"

class TestGCPEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """Base URL for the GCP deployment."""
        return GCP_BASE_URL

    @pytest.fixture(scope="class")
    def session(self) -> requests.Session:
        """HTTP session with default configuration."""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "NeMo-Guardrails-EdgeCase-Test/1.0"
        })
        return session

    def test_empty_and_whitespace_inputs(self, base_url: str, session: requests.Session):
        """Test handling of empty and whitespace-only inputs."""
        edge_inputs = [
            "",  # Completely empty
            " ",  # Single space
            "   ",  # Multiple spaces
            "\t",  # Tab character
            "\n",  # Newline
            "\r\n",  # Windows newline
            "\t\n\r ",  # Mixed whitespace
        ]
        
        for i, test_input in enumerate(edge_inputs):
            payload = {
                "messages": [{"role": "user", "content": test_input}]
            }
            
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=15
                )
                
                # Should handle gracefully (either process or reject appropriately)
                assert response.status_code in [200, 400], f"Whitespace test {i}: unexpected status {response.status_code}"
                
                if response.status_code == 200:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        result = response.json()
                        if "messages" in result and result["messages"]:
                            content = result["messages"][-1]["content"]
                            # Should provide some response, not just echo whitespace
                            assert len(content.strip()) > 0, f"Should provide meaningful response to whitespace input {i}"
                
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Whitespace test {i} failed: {e}")

    def test_very_long_inputs(self, base_url: str, session: requests.Session):
        """Test handling of very long input messages."""
        # Test different lengths
        test_lengths = [1000, 5000, 10000, 50000]  # characters
        
        for length in test_lengths:
            long_message = "This is a very long test message. " * (length // 34 + 1)
            long_message = long_message[:length]  # Trim to exact length
            
            payload = {
                "messages": [{"role": "user", "content": long_message}]
            }
            
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=60  # Longer timeout for large inputs
                )
                
                # Should either process or reject with appropriate status
                assert response.status_code in [200, 400, 413, 414], \
                       f"Long input ({length} chars): unexpected status {response.status_code}"
                
                if response.status_code == 200:
                    # Should respond within reasonable time even for long inputs
                    assert response.elapsed.total_seconds() < 45, \
                           f"Long input processing too slow: {response.elapsed.total_seconds():.2f}s"
                
                print(f"Length {length}: HTTP {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                
            except requests.exceptions.RequestException as e:
                if "timeout" in str(e).lower():
                    print(f"Length {length}: Request timeout (expected for very long inputs)")
                else:
                    pytest.fail(f"Long input test ({length} chars) failed: {e}")

    def test_special_characters_and_encoding(self, base_url: str, session: requests.Session):
        """Test handling of special characters and various encodings."""
        special_inputs = [
            "Hello 🌍🚀💻 Unicode test",
            "Special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "Math symbols: ∑∏∫∂∇∆√∞≈≠≤≥±×÷",
            "Currency: $¢£¤¥₦₹€₿",
            "Quotes: \"'`""''‚„‹›«»",
            "Dashes: -–—",
            "Spaces: regular thin hair em en figure punctuation",
            "Control chars: \x00\x01\x02\x03",  # Control characters
            "Mixed: Hello世界 Здравствуй мир مرحبا بالعالم",
            "Emoji combo: 👨‍💻👩‍🔬🧑‍🎨",
            "RTL text: مرحبا بك في هذا الاختبار",
            "Zero-width chars: \u200b\u200c\u200d\ufeff",
        ]
        
        for i, test_input in enumerate(special_inputs):
            payload = {
                "messages": [{"role": "user", "content": test_input}]
            }
            
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=30
                )
                
                # Should handle special characters gracefully
                assert response.status_code in [200, 400], \
                       f"Special chars test {i}: unexpected status {response.status_code}"
                
                if response.status_code == 200:
                    if response.headers.get('content-type', '').startswith('application/json'):
                        result = response.json()
                        if "messages" in result and result["messages"]:
                            content = result["messages"][-1]["content"]
                            # Should provide meaningful response
                            assert len(content.strip()) > 0, f"Should respond to special chars input {i}"
                
            except (requests.exceptions.RequestException, UnicodeError) as e:
                # Unicode errors might occur with control characters
                if "control" in test_input.lower() or "\\x" in test_input:
                    print(f"Special chars test {i}: Expected encoding issue with control chars")
                else:
                    pytest.fail(f"Special chars test {i} failed: {e}")

    def test_malformed_json_payloads(self, base_url: str, session: requests.Session):
        """Test handling of malformed JSON payloads."""
        # Use raw requests to send malformed JSON
        malformed_payloads = [
            '{"messages": [{"role": "user", "content": "test"}',  # Missing closing brace
            '{"messages": [{"role": "user" "content": "test"}]}',  # Missing comma
            '{"messages": [{"role": "user", "content": "test"]}]',  # Extra bracket
            '{"messages": [{"role": "user", "content": }]}',  # Missing value
            '{"messages": [{"role": "user", "content": "test"""}]}',  # Extra quote
            '{messages: [{"role": "user", "content": "test"}]}',  # Unquoted key
            '',  # Empty payload
            'not json at all',  # Not JSON
            '{"messages": null}',  # Null messages
            '{"messages": "not an array"}',  # Wrong type
        ]
        
        for i, malformed_json in enumerate(malformed_payloads):
            try:
                response = requests.post(
                    f"{base_url}/v1/chat/completions",
                    data=malformed_json,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "NeMo-Guardrails-EdgeCase-Test/1.0"
                    },
                    timeout=15
                )
                
                # Should return 400 Bad Request for malformed JSON
                assert response.status_code == 400, \
                       f"Malformed JSON {i}: expected 400, got {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Malformed JSON test {i} failed: {e}")

    def test_unusual_http_methods(self, base_url: str, session: requests.Session):
        """Test handling of unusual HTTP methods."""
        unusual_methods = ["PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
        
        payload = {
            "messages": [{"role": "user", "content": "Test with unusual method"}]
        }
        
        for method in unusual_methods:
            try:
                response = session.request(
                    method,
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=15
                )
                
                # Should return 405 Method Not Allowed or similar
                assert response.status_code in [405, 501, 404], \
                       f"Method {method}: expected 4xx/5xx, got {response.status_code}"
                
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Unusual method test ({method}) failed: {e}")

    def test_missing_required_fields(self, base_url: str, session: requests.Session):
        """Test handling of requests with missing required fields."""
        invalid_payloads = [
            {},  # Completely empty
            {"messages": []},  # Empty messages array
            {"messages": [{}]},  # Message without required fields
            {"messages": [{"role": "user"}]},  # Missing content
            {"messages": [{"content": "test"}]},  # Missing role
            {"messages": [{"role": "invalid", "content": "test"}]},  # Invalid role
            {"messages": [{"role": "", "content": "test"}]},  # Empty role
            {"messages": [{"role": "user", "content": ""}]},  # Empty content
            {"invalid_field": "value"},  # Wrong top-level field
            {"messages": "not an array"},  # Wrong type for messages
        ]
        
        for i, payload in enumerate(invalid_payloads):
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=15
                )
                
                # Should return 400 Bad Request
                assert response.status_code == 400, \
                       f"Invalid payload {i}: expected 400, got {response.status_code}"
                
                # Should provide informative error message
                if response.headers.get('content-type', '').startswith('application/json'):
                    error_data = response.json()
                    assert "error" in error_data or "message" in error_data, \
                           f"Invalid payload {i}: should provide error details"
                
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Invalid payload test {i} failed: {e}")

    def test_rapid_successive_requests(self, base_url: str, session: requests.Session):
        """Test handling of rapid successive requests."""
        payload = {
            "messages": [{"role": "user", "content": "Rapid request test"}]
        }
        
        # Send requests as fast as possible
        responses = []
        start_time = time.time()
        
        for i in range(10):
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=30
                )
                responses.append({
                    "index": i,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                })
            except requests.exceptions.RequestException as e:
                responses.append({
                    "index": i,
                    "error": str(e)
                })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_responses = [r for r in responses if "status_code" in r and r["status_code"] == 200]
        success_rate = len(successful_responses) / len(responses)
        
        # Should handle most rapid requests successfully
        assert success_rate >= 0.6, f"Rapid requests success rate too low: {success_rate:.2%}"
        
        # Calculate requests per second
        rps = len(responses) / total_time
        print(f"Rapid requests - RPS: {rps:.1f}, Success rate: {success_rate:.2%}")

    def test_timeout_behavior(self, base_url: str, session: requests.Session):
        """Test behavior with very short timeouts."""
        payload = {
            "messages": [{"role": "user", "content": "Timeout test with a complex question that requires detailed analysis and explanation"}]
        }
        
        # Test with very short timeout
        try:
            response = session.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                timeout=0.1  # 100ms timeout
            )
            
            # If it succeeds, it's very fast
            print(f"Request completed in under 100ms: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print("Request properly timed out as expected")
        except requests.exceptions.RequestException as e:
            print(f"Request failed with: {e}")

    def test_concurrent_identical_requests(self, base_url: str, session: requests.Session):
        """Test handling of many identical concurrent requests."""
        import concurrent.futures
        
        payload = {
            "messages": [{"role": "user", "content": "Identical concurrent request test"}]
        }
        
        def make_request():
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=30
                )
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
            except requests.exceptions.RequestException as e:
                return {"success": False, "error": str(e)}
        
        # Launch 10 identical requests simultaneously (reduced for faster testing)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        successful_requests = [r for r in results if r["success"]]
        success_rate = len(successful_requests) / len(results)
        
        assert success_rate >= 0.6, f"Identical concurrent requests success rate too low: {success_rate:.2%}"
        
        if successful_requests:
            avg_response_time = sum(r["response_time"] for r in successful_requests) / len(successful_requests)
            print(f"Identical concurrent requests - Success: {success_rate:.2%}, Avg time: {avg_response_time:.2f}s")

class TestGCPErrorRecovery:
    """Test error recovery and resilience mechanisms."""

    @pytest.fixture(scope="class")
    def session(self) -> requests.Session:
        """HTTP session for error recovery tests."""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "NeMo-Guardrails-Recovery-Test/1.0"
        })
        return session

    def test_service_recovery_after_errors(self, session: requests.Session):
        """Test that service recovers properly after error conditions."""
        base_url = GCP_BASE_URL
        
        # First, cause some errors
        error_payloads = [
            {},  # Empty payload
            {"messages": []},  # Empty messages
            {"messages": [{"role": "invalid", "content": "test"}]},  # Invalid role
        ]
        
        # Generate errors
        for payload in error_payloads:
            try:
                session.post(
                    f"{base_url}/v1/chat/completions",
                    json=payload,
                    timeout=15
                )
            except Exception:
                pass  # Ignore errors for this test
        
        # Now test that service still works normally
        good_payload = {
            "messages": [{"role": "user", "content": "Recovery test - service should work normally"}]
        }
        
        recovery_attempts = 3
        successful_recoveries = 0
        
        for i in range(recovery_attempts):
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=good_payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    successful_recoveries += 1
                
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)  # Brief pause between recovery attempts
        
        recovery_rate = successful_recoveries / recovery_attempts
        assert recovery_rate >= 0.8, f"Service recovery rate too low: {recovery_rate:.2%}"
        
        print(f"Service recovery rate: {recovery_rate:.2%}")

    def test_graceful_degradation(self, session: requests.Session):
        """Test graceful degradation under stress."""
        base_url = GCP_BASE_URL
        
        # Create stress by sending many requests quickly
        stress_payload = {
            "messages": [{"role": "user", "content": "Stress test for graceful degradation"}]
        }
        
        responses = []
        for i in range(20):  # 20 rapid requests
            try:
                response = session.post(
                    f"{base_url}/v1/chat/completions",
                    json=stress_payload,
                    timeout=10  # Shorter timeout under stress
                )
                responses.append(response.status_code)
            except requests.exceptions.RequestException:
                responses.append(None)  # Failed request
        
        # Under stress, should either:
        # 1. Process requests successfully (200)
        # 2. Return rate limiting (429)
        # 3. Return service unavailable (503)
        # Should not crash or return 5xx errors (except 503)
        
        status_codes = [code for code in responses if code is not None]
        if status_codes:
            valid_stress_codes = [200, 400, 429, 503]
            invalid_codes = [code for code in status_codes if code not in valid_stress_codes]
            
            assert len(invalid_codes) == 0, f"Found invalid stress response codes: {invalid_codes}"
            
            success_rate = status_codes.count(200) / len(status_codes)
            print(f"Stress test - Success rate: {success_rate:.2%}, Status codes: {set(status_codes)}")

def run_edge_case_tests():
    """Run all edge case tests."""
    return pytest.main([__file__, "-v", "--tb=short", "-s"])

if __name__ == "__main__":
    run_edge_case_tests()