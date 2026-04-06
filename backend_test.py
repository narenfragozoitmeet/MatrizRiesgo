#!/usr/bin/env python3
"""
Backend API Testing for Sistema de Matrices de Riesgos
Tests the actual implemented endpoints based on the unified_api.py
"""

import requests
import sys
import json
import os
from datetime import datetime

class MatrizRiesgosAPITester:
    def __init__(self):
        # Get backend URL from frontend .env file
        self.base_url = "https://hazard-assess-pro-1.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test_result(self, test_name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   {details}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: FAILED")
            if details:
                print(f"   {details}")

    def test_root_endpoint(self):
        """Test GET / endpoint - Note: External URL serves frontend, backend root is at localhost:8001"""
        print(f"\n🔍 Testing Root Endpoint...")
        try:
            # Test external URL - should serve React frontend (HTML)
            response = requests.get(self.base_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                if "<!doctype html>" in content.lower() and "div id=\"root\"" in content:
                    self.log_test_result(
                        "Root Endpoint (Frontend)", 
                        True, 
                        "Correctly serves React frontend at root path"
                    )
                    
                    # Also test internal backend root endpoint
                    try:
                        backend_response = requests.get("http://localhost:8001/", timeout=10)
                        if backend_response.status_code == 200:
                            backend_data = backend_response.json()
                            expected_fields = ["app", "version", "status", "tipos_matrices", "metodologias", "llm"]
                            
                            missing_fields = [field for field in expected_fields if field not in backend_data]
                            if not missing_fields:
                                self.log_test_result(
                                    "Backend Root (Internal)", 
                                    True, 
                                    f"App: {backend_data.get('app')}, Version: {backend_data.get('version')}"
                                )
                                return True
                            else:
                                self.log_test_result(
                                    "Backend Root (Internal)", 
                                    False, 
                                    f"Missing fields: {missing_fields}"
                                )
                        else:
                            self.log_test_result(
                                "Backend Root (Internal)", 
                                False, 
                                f"Expected 200, got {backend_response.status_code}"
                            )
                    except Exception as e:
                        self.log_test_result("Backend Root (Internal)", False, f"Exception: {str(e)}")
                        return True  # Still pass if frontend works
                    
                else:
                    self.log_test_result(
                        "Root Endpoint", 
                        False, 
                        f"Expected HTML frontend with React root div, got: {content[:200]}"
                    )
            else:
                self.log_test_result(
                    "Root Endpoint", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test_result("Root Endpoint", False, f"Exception: {str(e)}")
        
        return False

    def test_health_endpoint(self):
        """Test GET /api/health endpoint"""
        print(f"\n🔍 Testing Health Check Endpoint...")
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "database", "llm"]
                
                missing_fields = [field for field in expected_fields if field not in data]
                if missing_fields:
                    self.log_test_result(
                        "Health Check", 
                        False, 
                        f"Missing fields: {missing_fields}"
                    )
                else:
                    db_status = data.get('database', 'unknown')
                    app_status = data.get('status', 'unknown')
                    
                    if db_status == 'connected' and app_status == 'healthy':
                        self.log_test_result(
                            "Health Check", 
                            True, 
                            f"Status: {app_status}, Database: {db_status}, LLM: {data.get('llm')}"
                        )
                        return True
                    else:
                        self.log_test_result(
                            "Health Check", 
                            False, 
                            f"Unhealthy - Status: {app_status}, Database: {db_status}"
                        )
            else:
                self.log_test_result(
                    "Health Check", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test_result("Health Check", False, f"Exception: {str(e)}")
        
        return False

    def test_api_docs(self):
        """Test GET /api/docs endpoint (Swagger UI)"""
        print(f"\n🔍 Testing API Documentation...")
        try:
            response = requests.get(f"{self.api_url}/docs", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                # Check if it's actually Swagger UI
                if "swagger" in content.lower() or "openapi" in content.lower():
                    self.log_test_result(
                        "API Documentation", 
                        True, 
                        f"Swagger UI accessible, content length: {len(content)} chars"
                    )
                    return True
                else:
                    self.log_test_result(
                        "API Documentation", 
                        False, 
                        "Response doesn't appear to be Swagger UI"
                    )
            else:
                self.log_test_result(
                    "API Documentation", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test_result("API Documentation", False, f"Exception: {str(e)}")
        
        return False

    def test_list_matrices_empty(self):
        """Test GET /api/v1/matrices endpoint (should be empty initially)"""
        print(f"\n🔍 Testing List Matrices Endpoint...")
        try:
            response = requests.get(f"{self.api_url}/v1/matrices", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_test_result(
                        "List Matrices", 
                        True, 
                        f"Returned list with {len(data)} matrices"
                    )
                    return True
                else:
                    self.log_test_result(
                        "List Matrices", 
                        False, 
                        f"Expected list, got {type(data)}: {str(data)[:200]}"
                    )
            else:
                self.log_test_result(
                    "List Matrices", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test_result("List Matrices", False, f"Exception: {str(e)}")
        
        return False

    def test_list_matrices_with_filter(self):
        """Test GET /api/v1/matrices?tipo=sst endpoint"""
        print(f"\n🔍 Testing List Matrices with Filter...")
        try:
            response = requests.get(f"{self.api_url}/v1/matrices?tipo=sst", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list):
                    self.log_test_result(
                        "List Matrices (SST Filter)", 
                        True, 
                        f"Returned list with {len(data)} SST matrices"
                    )
                    return True
                else:
                    self.log_test_result(
                        "List Matrices (SST Filter)", 
                        False, 
                        f"Expected list, got {type(data)}: {str(data)[:200]}"
                    )
            else:
                self.log_test_result(
                    "List Matrices (SST Filter)", 
                    False, 
                    f"Expected 200, got {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test_result("List Matrices (SST Filter)", False, f"Exception: {str(e)}")
        
        return False

    def test_nonexistent_matrix(self):
        """Test GET /api/v1/matrix/sst/nonexistent-id endpoint"""
        print(f"\n🔍 Testing Non-existent Matrix...")
        try:
            response = requests.get(f"{self.api_url}/v1/matrix/sst/nonexistent-id", timeout=10)
            
            if response.status_code == 404:
                self.log_test_result(
                    "Non-existent Matrix", 
                    True, 
                    "Correctly returned 404 for non-existent matrix"
                )
                return True
            else:
                self.log_test_result(
                    "Non-existent Matrix", 
                    False, 
                    f"Expected 404, got {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test_result("Non-existent Matrix", False, f"Exception: {str(e)}")
        
        return False

    def test_invalid_matrix_type(self):
        """Test GET /api/v1/matrix/invalid/some-id endpoint"""
        print(f"\n🔍 Testing Invalid Matrix Type...")
        try:
            response = requests.get(f"{self.api_url}/v1/matrix/invalid/some-id", timeout=10)
            
            if response.status_code == 400:
                self.log_test_result(
                    "Invalid Matrix Type", 
                    True, 
                    "Correctly returned 400 for invalid matrix type"
                )
                return True
            else:
                self.log_test_result(
                    "Invalid Matrix Type", 
                    False, 
                    f"Expected 400, got {response.status_code}: {response.text[:200]}"
                )
        except Exception as e:
            self.log_test_result("Invalid Matrix Type", False, f"Exception: {str(e)}")
        
        return False

    def check_backend_logs(self):
        """Check backend logs for any errors"""
        print(f"\n🔍 Checking Backend Logs...")
        try:
            import subprocess
            result = subprocess.run(
                ["tail", "-n", "50", "/var/log/supervisor/backend.err.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logs = result.stdout
                if logs.strip():
                    print(f"📋 Recent backend error logs:")
                    print(logs[-1000:])  # Last 1000 chars
                else:
                    print("📋 No recent error logs found")
            else:
                print(f"⚠️ Could not read backend logs: {result.stderr}")
                
        except Exception as e:
            print(f"⚠️ Error checking logs: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Tests for Sistema de Matrices de Riesgos")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 70)

        # Test sequence - basic endpoints only as requested
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Health Check", self.test_health_endpoint),
            ("API Documentation", self.test_api_docs),
            ("List Matrices (Empty)", self.test_list_matrices_empty),
            ("List Matrices (SST Filter)", self.test_list_matrices_with_filter),
            ("Non-existent Matrix", self.test_nonexistent_matrix),
            ("Invalid Matrix Type", self.test_invalid_matrix_type),
        ]

        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"Unexpected exception: {str(e)}")

        # Check logs for any issues
        self.check_backend_logs()

        # Print final results
        print("\n" + "=" * 70)
        print(f"📊 FINAL TEST RESULTS")
        print("=" * 70)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {len(self.failed_tests)}")
        
        if self.failed_tests:
            print(f"Failed tests: {', '.join(self.failed_tests)}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️ Some tests failed")
            return False

def main():
    tester = MatrizRiesgosAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())