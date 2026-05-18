#!/usr/bin/env python3
"""
Smoke test for TaskManager application.

Quick integration test to verify the application is running and responding.
"""

import sys
import time
import requests
from typing import Dict, Any


class TaskManagerSmokeTest:
    """
    Smoke test class for TaskManager application.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 10  # 10 second timeout
        self.results = []
    
    def test_endpoint(self, endpoint: str, method: str = "GET", expected_status: int = 200) -> bool:
        """
        Test a single endpoint.
        
        Args:
            endpoint: API endpoint to test
            method: HTTP method (GET, POST, etc.)
            expected_status: Expected HTTP status code
            
        Returns:
            True if test passed, False otherwise
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            print(f"Testing {method} {url}")
            
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=self.timeout)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=self.timeout)
            else:
                print(f"Unsupported method: {method}")
                return False
            
            end_time = time.time()
            response_time = end_time - start_time
            
            success = response.status_code == expected_status
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "response_time": response_time,
                "response_size": len(response.content),
                "error": None if success else f"Expected {expected_status}, got {response.status_code}"
            }
            
            self.results.append(result)
            
            if success:
                print(f"✓ {method} {url} - {response.status_code} ({response_time:.3f}s)")
            else:
                print(f"✗ {method} {url} - {response.status_code} (expected {expected_status})")
            
            return success
            
        except requests.exceptions.Timeout:
            print(f"✗ {method} {url} - Timeout after {self.timeout}s")
            result = {
                "endpoint": endpoint,
                "method": method,
                "url": url,
                "status_code": None,
                "expected_status": expected_status,
                "success": False,
                "response_time": self.timeout,
                "response_size": 0,
                "error": f"Timeout after {self.timeout}s"
            }
            self.results.append(result)
            return False
            
        except requests.exceptions.ConnectionError as e:
            print(f"✗ {method} {url} - Connection error: {e}")
            result = {
                "endpoint": endpoint,
                "method": method,
                "url": url,
                "status_code": None,
                "expected_status": expected_status,
                "success": False,
                "response_time": 0,
                "response_size": 0,
                "error": f"Connection error: {e}"
            }
            self.results.append(result)
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test the health endpoint."""
        return self.test_endpoint("/api/health")
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        return self.test_endpoint("/")
    
    def test_docs_endpoint(self) -> bool:
        """Test the API docs endpoint."""
        return self.test_endpoint("/docs")
    
    def test_redoc_endpoint(self) -> bool:
        """Test the ReDoc endpoint."""
        return self.test_endpoint("/redoc")
    
    def test_openapi_endpoint(self) -> bool:
        """Test the OpenAPI endpoint."""
        return self.test_endpoint("/openapi.json")
    
    def test_ping_endpoint(self) -> bool:
        """Test the ping endpoint."""
        return self.test_endpoint("/api/health/ping")
    
    def test_detailed_health_endpoint(self) -> bool:
        """Test the detailed health endpoint."""
        return self.test_endpoint("/api/health/detailed")
    
    def test_tasks_endpoint(self) -> bool:
        """Test the tasks endpoint (should work without authentication for now)."""
        return self.test_endpoint("/api/tasks")
    
    def test_categories_endpoint(self) -> bool:
        """Test the categories endpoint (should work without authentication for now)."""
        return self.test_endpoint("/api/categories")
    
    def test_invalid_endpoint(self) -> bool:
        """Test an invalid endpoint (should return 404)."""
        return self.test_endpoint("/api/invalid", expected_status=404)
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run all smoke tests.
        
        Returns:
            Test results summary
        """
        print("🚀 Starting TaskManager smoke tests...")
        print(f"Base URL: {self.base_url}")
        print("-" * 50)
        
        # List of tests to run
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Health Endpoint", self.test_health_endpoint),
            ("Ping Endpoint", self.test_ping_endpoint),
            ("Detailed Health Endpoint", self.test_detailed_health_endpoint),
            ("API Docs", self.test_docs_endpoint),
            ("ReDoc", self.test_redoc_endpoint),
            ("OpenAPI Schema", self.test_openapi_endpoint),
            ("Tasks Endpoint", self.test_tasks_endpoint),
            ("Categories Endpoint", self.test_categories_endpoint),
            ("Invalid Endpoint", self.test_invalid_endpoint),
        ]
        
        # Run all tests
        test_results = []
        for name, test_func in tests:
            try:
                result = test_func()
                test_results.append((name, result))
            except Exception as e:
                print(f"✗ {name} - Exception: {e}")
                test_results.append((name, False))
        
        # Calculate summary
        total_tests = len(test_results)
        passed_tests = sum(1 for _, result in test_results if result)
        failed_tests = total_tests - passed_tests
        
        # Calculate average response time
        avg_response_time = sum(r["response_time"] for r in self.results if "response_time" in r) / len(self.results) if self.results else 0
        
        # Print summary
        print("-" * 50)
        print("📊 Test Results Summary:")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
        print(f"Average response time: {avg_response_time:.3f}s")
        
        # Print detailed results
        print("\n📋 Detailed Results:")
        for name, result in test_results:
            status = "✓ PASS" if result else "✗ FAIL"
            print(f"{status}: {name}")
        
        # Print failed tests details
        if failed_tests > 0:
            print("\n❌ Failed Tests Details:")
            for result in self.results:
                if not result["success"]:
                    print(f"  {result['endpoint']} ({result['method']}): {result['error']}")
        
        # Return summary
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "average_response_time": avg_response_time,
            "results": self.results,
            "test_details": test_results
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = "smoke_test_results.json"):
        """Save test results to a JSON file."""
        import json
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Test results saved to: {filename}")
    
    def print_results_table(self, results: Dict[str, Any]):
        """Print results in a formatted table."""
        print("\n" + "=" * 80)
        print("📊 SMOKE TEST RESULTS")
        print("=" * 80)
        
        # Header
        print(f"{'Test Name':<30} {'Status':<10} {'Response Time':<15} {'Size (bytes)':<12}")
        print("-" * 80)
        
        # Results
        for result in self.results:
            status = "PASS" if result["success"] else "FAIL"
            response_time = f"{result['response_time']:.3f}s"
            size = f"{result['response_size']}"
            
            print(f"{result['endpoint']:<30} {status:<10} {response_time:<15} {size:<12}")
        
        # Summary
        print("-" * 80)
        print(f"Total: {results['total_tests']}, Passed: {results['passed_tests']}, Failed: {results['failed_tests']}")
        print(f"Success Rate: {results['success_rate']*100:.1f}%")
        print(f"Average Response Time: {results['average_response_time']:.3f}s")
        print("=" * 80)


def main():
    """
    Main function to run smoke tests.
    """
    # Parse command line arguments
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    # Create test instance
    smoke_test = TaskManagerSmokeTest(base_url)
    
    # Run tests
    results = smoke_test.run_all_tests()
    
    # Save results
    smoke_test.save_results(results)
    
    # Print formatted results
    smoke_test.print_results_table(results)
    
    # Exit with appropriate code
    if results["failed_tests"] > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()