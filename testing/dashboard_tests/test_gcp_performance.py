#!/usr/bin/env python3
"""
Performance and load testing for NeMo Guardrails GCP deployment at http://34.83.192.203/
Tests throughput, latency, concurrent users, and system behavior under load.
"""

import pytest
import requests
import time
import statistics
import concurrent.futures
import threading
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass

# GCP deployment base URL (actual API service)
GCP_BASE_URL = "https://api.garaksecurity.com"

@dataclass
class PerformanceMetrics:
    """Data class for storing performance test results."""
    response_times: List[float]
    success_count: int
    total_requests: int
    errors: List[str]
    
    @property
    def success_rate(self) -> float:
        return self.success_count / self.total_requests if self.total_requests > 0 else 0.0
    
    @property
    def average_response_time(self) -> float:
        return statistics.mean(self.response_times) if self.response_times else 0.0
    
    @property
    def median_response_time(self) -> float:
        return statistics.median(self.response_times) if self.response_times else 0.0
    
    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[min(index, len(sorted_times) - 1)]

class TestGCPPerformance:
    """Performance testing suite for GCP deployment."""

    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """Base URL for the GCP deployment."""
        return GCP_BASE_URL

    @pytest.fixture(scope="class")
    def session(self) -> requests.Session:
        """HTTP session with connection pooling."""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "NeMo-Guardrails-Performance-Test/1.0"
        })
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=3
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _make_request(self, session: requests.Session, base_url: str, 
                     message: str, timeout: int = 30) -> Tuple[bool, float, str]:
        """Make a single request and return success, response time, and error."""
        payload = {
            "messages": [{"role": "user", "content": message}]
        }
        
        start_time = time.time()
        try:
            response = session.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                timeout=timeout
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response.status_code == 200
            error_msg = f"HTTP {response.status_code}" if not success else ""
            
            return success, response_time, error_msg
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = end_time - start_time
            return False, response_time, str(e)

    def test_basic_response_time(self, base_url: str, session: requests.Session):
        """Test basic response time for simple requests."""
        test_message = "Hello, this is a performance test."
        
        success, response_time, error = self._make_request(session, base_url, test_message)
        
        assert success, f"Basic request failed: {error}"
        assert response_time < 10.0, f"Response time too slow: {response_time:.2f}s"
        
        print(f"Basic response time: {response_time:.2f}s")

    def test_complex_query_performance(self, base_url: str, session: requests.Session):
        """Test performance with complex queries."""
        complex_message = """
        Can you explain the differences between machine learning, deep learning, and artificial intelligence?
        Please provide examples of each and explain how they relate to each other in the context of modern
        technology applications. Also discuss the current limitations and future prospects of these fields.
        """
        
        success, response_time, error = self._make_request(session, base_url, complex_message, timeout=45)
        
        assert success, f"Complex query failed: {error}"
        assert response_time < 30.0, f"Complex query response time too slow: {response_time:.2f}s"
        
        print(f"Complex query response time: {response_time:.2f}s")

    def test_concurrent_users(self, base_url: str, session: requests.Session):
        """Test system behavior with concurrent users."""
        num_concurrent_users = 10
        requests_per_user = 3
        test_message = "This is a concurrent user test message."
        
        def user_session():
            user_metrics = PerformanceMetrics([], 0, 0, [])
            
            for _ in range(requests_per_user):
                success, response_time, error = self._make_request(session, base_url, test_message)
                
                user_metrics.total_requests += 1
                if success:
                    user_metrics.success_count += 1
                    user_metrics.response_times.append(response_time)
                else:
                    user_metrics.errors.append(error)
                
                time.sleep(0.1)  # Brief pause between requests
            
            return user_metrics
        
        # Run concurrent user sessions
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_users) as executor:
            futures = [executor.submit(user_session) for _ in range(num_concurrent_users)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Aggregate results
        total_requests = sum(r.total_requests for r in results)
        total_successes = sum(r.success_count for r in results)
        all_response_times = []
        all_errors = []
        
        for result in results:
            all_response_times.extend(result.response_times)
            all_errors.extend(result.errors)
        
        success_rate = total_successes / total_requests if total_requests > 0 else 0.0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0.0
        
        assert success_rate >= 0.8, f"Concurrent user success rate too low: {success_rate:.2%}"
        assert avg_response_time < 15.0, f"Average response time under load too slow: {avg_response_time:.2f}s"
        
        print(f"Concurrent users - Success rate: {success_rate:.2%}, Avg response time: {avg_response_time:.2f}s")

    def test_sustained_load(self, base_url: str, session: requests.Session):
        """Test system behavior under sustained load."""
        duration_seconds = 30  # 30 seconds sustained test (reduced for faster testing)
        request_interval = 3.0  # Request every 3 seconds
        test_message = "Sustained load test message."
        
        metrics = PerformanceMetrics([], 0, 0, [])
        start_test_time = time.time()
        
        while time.time() - start_test_time < duration_seconds:
            success, response_time, error = self._make_request(session, base_url, test_message)
            
            metrics.total_requests += 1
            if success:
                metrics.success_count += 1
                metrics.response_times.append(response_time)
            else:
                metrics.errors.append(error)
            
            time.sleep(request_interval)
        
        assert metrics.success_rate >= 0.9, f"Sustained load success rate too low: {metrics.success_rate:.2%}"
        assert metrics.average_response_time < 10.0, f"Average response time under sustained load too slow: {metrics.average_response_time:.2f}s"
        
        print(f"Sustained load - Requests: {metrics.total_requests}, Success rate: {metrics.success_rate:.2%}")
        print(f"Avg response time: {metrics.average_response_time:.2f}s, P95: {metrics.p95_response_time:.2f}s")

    def test_burst_traffic(self, base_url: str, session: requests.Session):
        """Test system behavior with burst traffic patterns."""
        burst_size = 20
        test_message = "Burst traffic test message."
        
        def make_burst_request():
            return self._make_request(session, base_url, test_message)
        
        # Create burst of concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=burst_size) as executor:
            futures = [executor.submit(make_burst_request) for _ in range(burst_size)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        total_time = end_time - start_time
        successes = sum(1 for success, _, _ in results if success)
        response_times = [rt for success, rt, _ in results if success]
        errors = [error for success, _, error in results if not success]
        
        success_rate = successes / burst_size
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        requests_per_second = burst_size / total_time
        
        assert success_rate >= 0.7, f"Burst traffic success rate too low: {success_rate:.2%}"
        assert avg_response_time < 20.0, f"Burst traffic response time too slow: {avg_response_time:.2f}s"
        
        print(f"Burst traffic - RPS: {requests_per_second:.1f}, Success rate: {success_rate:.2%}")
        print(f"Avg response time: {avg_response_time:.2f}s")

    def test_large_payload_performance(self, base_url: str, session: requests.Session):
        """Test performance with large input payloads."""
        # Create a large message (approximately 2KB)
        large_message = "This is a performance test with a large payload. " * 40
        
        success, response_time, error = self._make_request(session, base_url, large_message, timeout=45)
        
        # Large payloads might be rejected or take longer
        if success:
            assert response_time < 30.0, f"Large payload response time too slow: {response_time:.2f}s"
            print(f"Large payload response time: {response_time:.2f}s")
        else:
            # If rejected, should be handled gracefully
            assert "413" in error or "400" in error, f"Large payload should be rejected gracefully, got: {error}"
            print(f"Large payload appropriately rejected: {error}")

    def test_different_input_types_performance(self, base_url: str, session: requests.Session):
        """Test performance with different types of inputs."""
        test_cases = {
            "simple_greeting": "Hello!",
            "question": "What is artificial intelligence?",
            "complex_query": "Explain the relationship between quantum mechanics and general relativity in modern physics.",
            "creative_request": "Write a short story about a robot learning to paint.",
        }
        
        results = {}
        
        for test_name, message in test_cases.items():
            success, response_time, error = self._make_request(session, base_url, message)
            
            results[test_name] = {
                "success": success,
                "response_time": response_time,
                "error": error
            }
            
            if success:
                assert response_time < 25.0, f"{test_name} response time too slow: {response_time:.2f}s"
            
            time.sleep(1)  # Brief pause between different test types
        
        # Print performance summary
        for test_name, result in results.items():
            if result["success"]:
                print(f"{test_name}: {result['response_time']:.2f}s")
            else:
                print(f"{test_name}: FAILED - {result['error']}")

    def test_memory_leak_detection(self, base_url: str, session: requests.Session):
        """Test for potential memory leaks with repeated requests."""
        num_requests = 20  # Reduced for faster testing
        test_message = "Memory leak detection test."
        
        response_times = []
        success_count = 0
        
        for i in range(num_requests):
            success, response_time, error = self._make_request(session, base_url, test_message)
            
            if success:
                success_count += 1
                response_times.append(response_time)
            
            # Brief pause to allow cleanup
            time.sleep(0.1)
        
        success_rate = success_count / num_requests
        
        # Check that performance doesn't degrade significantly over time
        if len(response_times) >= 10:
            first_half = response_times[:len(response_times)//2]
            second_half = response_times[len(response_times)//2:]
            
            avg_first_half = statistics.mean(first_half)
            avg_second_half = statistics.mean(second_half)
            
            # Performance shouldn't degrade by more than 50%
            degradation_ratio = avg_second_half / avg_first_half if avg_first_half > 0 else 1.0
            
            assert degradation_ratio < 1.5, f"Performance degradation detected: {degradation_ratio:.2f}x slower"
            
            print(f"Memory leak test - Success rate: {success_rate:.2%}")
            print(f"First half avg: {avg_first_half:.2f}s, Second half avg: {avg_second_half:.2f}s")

class TestGCPScalability:
    """Scalability testing for GCP deployment."""

    @pytest.fixture(scope="class")
    def session(self) -> requests.Session:
        """HTTP session for scalability tests."""
        session = requests.Session()
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "NeMo-Guardrails-Scalability-Test/1.0"
        })
        return session

    def test_gradual_load_increase(self, session: requests.Session):
        """Test system behavior as load gradually increases."""
        base_url = GCP_BASE_URL
        test_message = "Gradual load increase test."
        
        load_levels = [1, 3, 5, 8, 10]  # Number of concurrent users
        results = {}
        
        for num_users in load_levels:
            print(f"Testing with {num_users} concurrent users...")
            
            def user_requests():
                success, response_time, error = self._make_request(session, base_url, test_message)
                return success, response_time
            
            # Run concurrent requests
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_users) as executor:
                futures = [executor.submit(user_requests) for _ in range(num_users)]
                load_results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            successes = sum(1 for success, _ in load_results if success)
            response_times = [rt for success, rt in load_results if success]
            
            success_rate = successes / num_users if num_users > 0 else 0.0
            avg_response_time = statistics.mean(response_times) if response_times else 0.0
            
            results[num_users] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time
            }
            
            time.sleep(2)  # Pause between load levels
        
        # Verify that system handles increasing load reasonably
        for num_users, result in results.items():
            assert result["success_rate"] >= 0.7, f"Load level {num_users} users: success rate too low"
            print(f"{num_users} users: {result['success_rate']:.2%} success, {result['avg_response_time']:.2f}s avg")

    def _make_request(self, session: requests.Session, base_url: str, 
                     message: str, timeout: int = 30) -> Tuple[bool, float]:
        """Make a single request and return success and response time."""
        payload = {
            "messages": [{"role": "user", "content": message}]
        }
        
        start_time = time.time()
        try:
            response = session.post(
                f"{base_url}/v1/chat/completions",
                json=payload,
                timeout=timeout
            )
            end_time = time.time()
            response_time = end_time - start_time
            
            return response.status_code == 200, response_time
            
        except requests.exceptions.RequestException:
            end_time = time.time()
            response_time = end_time - start_time
            return False, response_time

def run_performance_tests():
    """Run all performance tests."""
    return pytest.main([__file__, "-v", "--tb=short", "-s"])

if __name__ == "__main__":
    run_performance_tests()