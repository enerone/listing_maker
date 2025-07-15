#!/usr/bin/env python3

import requests
import json

def test_frontend_suggestions():
    """Test the frontend suggestions integration"""
    
    print("🧪 Testing Frontend Suggestions Integration...")
    
    # Test data for different categories
    test_cases = [
        {
            "name": "Electronics",
            "data": {
                "product_name": "Smartwatch Pro",
                "category": "Electronics",
                "features": [],
                "target_price": 199.99
            }
        },
        {
            "name": "Sports",
            "data": {
                "product_name": "Running Shoes",
                "category": "Sports",
                "features": [],
                "target_price": 89.99
            }
        },
        {
            "name": "Other",
            "data": {
                "product_name": "Kitchen Utensil",
                "category": "Other",
                "features": [],
                "target_price": 24.99
            }
        }
    ]
    
    # Expected fields that frontend requires
    expected_fields = [
        'category', 'keywords', 'features', 'target_audience', 'price_recommendations',
        'price_range', 'marketing_angles', 'dimensions', 'weight', 'materials',
        'colors', 'box_contents', 'use_cases', 'main_competitor', 'brand', 'compatibility'
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\n🧪 Testing {test_case['name']} Category...")
        
        try:
            response = requests.post(
                'http://localhost:8000/api/listings/suggestions',
                headers={'Content-Type': 'application/json'},
                json=test_case['data']
            )
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', {})
                
                # Check if all expected fields are present
                missing_fields = [field for field in expected_fields if field not in suggestions]
                
                if missing_fields:
                    print(f"❌ Missing fields in {test_case['name']}: {missing_fields}")
                    all_passed = False
                else:
                    print(f"✅ All {len(expected_fields)} fields present in {test_case['name']} suggestions")
                    
                # Show field count
                print(f"   📊 Total fields: {len(suggestions)}")
                
                # Show some sample fields
                print(f"   🏷️  Brand: {suggestions.get('brand', 'N/A')}")
                print(f"   🎯 Target audience: {suggestions.get('target_audience', 'N/A')}")
                print(f"   💰 Price range: {suggestions.get('price_range', {}).get('suggested', 'N/A')}")
                print(f"   🏆 Main competitor: {suggestions.get('main_competitor', 'N/A')}")
                
            else:
                print(f"❌ HTTP {response.status_code} for {test_case['name']}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error testing {test_case['name']}: {str(e)}")
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Frontend suggestions integration is working correctly.")
        print("✅ Backend endpoint provides all expected fields for frontend consumption.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    test_frontend_suggestions()
