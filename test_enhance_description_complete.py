#!/usr/bin/env python3
"""
Test completo del endpoint de mejora de descripción
"""

import requests
import json
import sys

def test_enhance_description():
    """
    Test completo del endpoint de mejora de descripción
    """
    url = "http://localhost:8000/api/listings/1/enhance-description"
    
    test_data = {
        "current_description": "Este es un smartwatch básico con pantalla LED",
        "product_info": {
            "product_name": "Smartwatch Deportivo",
            "category": "Electronics",
            "title": "Smartwatch Deportivo Avanzado con Monitor de Salud"
        }
    }
    
    print(f"🔍 Testing endpoint: {url}")
    print(f"📤 Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, timeout=60)
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"📝 Original description: {result.get('original_description', 'N/A')}")
            print(f"🚀 Enhanced description: {result.get('enhanced_description', 'N/A')[:200]}...")
            print(f"📏 Improvement ratio: {result.get('improvement_metrics', {}).get('improvement_ratio', 0):.2f}x")
            print(f"⏰ Enhanced at: {result.get('enhanced_at', 'N/A')}")
            
            return True
            
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    """Main function"""
    print("🧪 Testing Enhanced Description Endpoint")
    print("=" * 50)
    
    success = test_enhance_description()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
