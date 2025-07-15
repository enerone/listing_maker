#!/usr/bin/env python3
"""
Integration test script for the cleaned up Amazon Listings Generator
Tests all major endpoints and functionality
"""

import requests
import json
import time
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, data: Dict[str, Any] = None, description: str = "") -> bool:
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print(f"✅ SUCCESS: {method} {endpoint}")
                
                # Print key information from response
                if isinstance(json_response, dict):
                    if 'success' in json_response:
                        print(f"   Response success: {json_response['success']}")
                    if 'status' in json_response:
                        print(f"   Status: {json_response['status']}")
                    if 'listings' in json_response:
                        print(f"   Listings count: {len(json_response['listings'])}")
                    if 'suggestions' in json_response:
                        print(f"   Suggestions generated: ✅")
                        if 'category' in json_response['suggestions']:
                            print(f"   Category: {json_response['suggestions']['category']}")
                        if 'keywords' in json_response['suggestions']:
                            print(f"   Keywords: {len(json_response['suggestions']['keywords'])}")
                
                return True
                
            except json.JSONDecodeError:
                print(f"✅ SUCCESS: {method} {endpoint} (Non-JSON response)")
                return True
                
        else:
            print(f"❌ FAILED: {method} {endpoint}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR: Cannot connect to {url}")
        print("   Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {method} {endpoint}")
        print(f"   Exception: {str(e)}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Starting Integration Tests for Amazon Listings Generator")
    print(f"Testing server at: {BASE_URL}")
    
    # Test cases
    test_cases = [
        # Frontend endpoints
        ("GET", "/", {}, "Frontend root page"),
        ("GET", "/app.js", {}, "Frontend JavaScript file"),
        
        # API Health
        ("GET", "/api/listings/health", {}, "API health check"),
        
        # Listings management
        ("GET", "/api/listings/", {}, "List all listings"),
        ("GET", "/api/listings/metrics", {}, "Get system metrics"),
        
        # AI Suggestions (Main new feature)
        ("POST", "/api/listings/suggestions", {
            "product_name": "Smart Watch Pro",
            "category": "Electronics",
            "target_price": 299.99,
            "features": ["Heart rate monitoring", "GPS tracking", "Waterproof", "Long battery life"]
        }, "Generate AI suggestions for a product"),
        
        # Image search
        ("POST", "/api/listings/search-images", {
            "product_name": "Smartwatch",
            "category": "Electronics"
        }, "Search product images"),
        
        # Test different product types
        ("POST", "/api/listings/suggestions", {
            "product_name": "Yoga Mat",
            "category": "Sports",
            "target_price": 49.99,
            "features": ["Non-slip surface", "Eco-friendly", "Thick padding"]
        }, "Generate suggestions for sports product"),
        
        ("POST", "/api/listings/suggestions", {
            "product_name": "Coffee Maker",
            "category": "Home & Garden",
            "target_price": 179.99,
            "features": ["Programmable", "Auto-shutoff", "Glass carafe"]
        }, "Generate suggestions for home product"),
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    for method, endpoint, data, description in test_cases:
        if test_endpoint(method, endpoint, data, description):
            passed += 1
        else:
            failed += 1
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print(f"\n{'='*60}")
    print("🎯 INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! The system is ready for production.")
        return 0
    else:
        print(f"\n⚠️  {failed} tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
