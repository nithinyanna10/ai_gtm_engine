#!/usr/bin/env python3
"""
Test each API endpoint individually.
"""

import requests
import time
import sys

API_BASE = "http://localhost:8000"

def test_api_endpoint(endpoint, method="GET", data=None):
    """Test a single API endpoint."""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        print(f"✅ {method} {endpoint}: {response.status_code}")
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, list):
                    print(f"   📊 Response: {len(result)} items")
                elif isinstance(result, dict):
                    print(f"   📊 Response: {list(result.keys())}")
                else:
                    print(f"   📊 Response: {result}")
            except:
                print(f"   📊 Response: {response.text[:100]}...")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"❌ {method} {endpoint}: TIMEOUT")
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint}: CONNECTION ERROR")
    except Exception as e:
        print(f"❌ {method} {endpoint}: {e}")

def main():
    """Test all API endpoints."""
    print("🧪 Testing AI GTM Engine APIs")
    print("=" * 40)
    
    # Test basic endpoints
    print("\n1. Basic API Endpoints:")
    test_api_endpoint("/health")
    test_api_endpoint("/docs")
    
    # Test leads endpoints
    print("\n2. Leads API Endpoints:")
    test_api_endpoint("/leads")
    test_api_endpoint("/leads?limit=5")
    
    # Test analytics endpoints
    print("\n3. Analytics API Endpoints:")
    test_api_endpoint("/analytics/overview")
    test_api_endpoint("/analytics/signals-by-type")
    
    # Test creating a lead
    print("\n4. Creating Test Lead:")
    test_lead = {
        "company_name": "Test Company",
        "domain": "test-company-api.com",
        "industry": "Technology",
        "employee_count": 100,
        "revenue_range": "10M-50M",
        "location": "Test City",
        "description": "Test company for API testing",
        "tech_stack": ["Python", "Django"],
        "primary_tech": "Python"
    }
    test_api_endpoint("/leads", method="POST", data=test_lead)
    
    # Test signal collection
    print("\n5. Testing Signal Collection:")
    test_api_endpoint("/leads/1/collect-signals", method="POST")
    
    print("\n🎉 API testing completed!")

if __name__ == "__main__":
    main()
