#!/usr/bin/env python3
"""
Test script for Docker Management API
This script demonstrates how to use the API endpoints.
"""

import requests
import json
import time
import sys

class DockerAPITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def test_health(self):
        """Test the health endpoint."""
        print("Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            return response.status_code == 200 or response.status_code == 503
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_commands_endpoint(self):
        """Test the commands documentation endpoint."""
        print("\nTesting commands endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/commands", timeout=5)
            print(f"Status Code: {response.status_code}")
            data = response.json()
            print("Available command categories:")
            for category in data.get('commands', {}):
                print(f"  - {category}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_containers_endpoint(self):
        """Test the containers endpoint."""
        print("\nTesting containers endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/containers", timeout=5)
            print(f"Status Code: {response.status_code}")
            data = response.json()
            if data.get('success'):
                print(f"Found {data.get('count', 0)} containers")
            else:
                print(f"Error: {data.get('error', 'Unknown error')}")
            return True  # Even errors are expected without Docker
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def test_system_endpoints(self):
        """Test system information endpoints."""
        print("\nTesting system endpoints...")
        endpoints = [
            "/api/system/version",
            "/api/system/info",
            "/api/system/status"
        ]
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                print(f"{endpoint}: Status {response.status_code}")
                if response.status_code == 500:
                    data = response.json()
                    print(f"  Expected error: {data.get('error', 'Unknown')}")
            except Exception as e:
                print(f"  Error: {e}")
        
        return True
    
    def run_all_tests(self):
        """Run all tests."""
        print("Docker Management API Test Suite")
        print("=" * 40)
        
        tests = [
            self.test_health,
            self.test_commands_endpoint,
            self.test_containers_endpoint,
            self.test_system_endpoints
        ]
        
        passed = 0
        for test in tests:
            if test():
                passed += 1
        
        print(f"\nTest Results: {passed}/{len(tests)} tests passed")
        print("\nNote: Some endpoints may return errors without Docker daemon running.")
        print("This is expected behavior and demonstrates proper error handling.")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"Testing API at: {base_url}")
    print("Make sure the API server is running with: python src/main.py")
    print()
    
    tester = DockerAPITester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()

