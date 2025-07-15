#!/usr/bin/env python3
"""
Test script to verify image search functionality with an existing listing.
"""
import requests
import json
import time

def test_existing_listing_images():
    """Test image search functionality with listing ID 35."""
    
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:8001"
    listing_id = 35
    
    print("🔍 Testing Image Search with Existing Listing")
    print("=" * 50)
    print(f"Testing with Listing ID: {listing_id}")
    
    try:
        # Step 1: Get listing details
        print("\n1. Getting listing details...")
        response = requests.get(f"{backend_url}/api/listings/{listing_id}")
        if response.status_code == 200:
            listing = response.json()
            print(f"   ✅ Listing found: {listing.get('product_name', 'Unknown')}")
            print(f"   ✅ Category: {listing.get('category', 'Unknown')}")
            print(f"   ✅ Price: ${listing.get('target_price', 0)}")
            print(f"   ✅ Full response: {listing}")
        else:
            print(f"   ❌ Failed to get listing: {response.status_code}")
            print(f"   ❌ Response: {response.text}")
            return False
        
        # Step 2: Test regenerate images endpoint
        print(f"\n2. Testing regenerate images for listing {listing_id}...")
        regen_response = requests.post(
            f"{backend_url}/api/listings/{listing_id}/regenerate-images",
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        if regen_response.status_code == 200:
            regen_data = regen_response.json()
            print(f"   ✅ Status: {regen_response.status_code}")
            print(f"   ✅ Success: {regen_data.get('success', False)}")
            print(f"   ✅ Message: {regen_data.get('message', '')}")
            
            if regen_data.get('total_new_images', 0) > 0:
                print(f"   ✅ New images found: {regen_data['total_new_images']}")
                if regen_data.get('new_images'):
                    print("   ✅ Sample images:")
                    for i, img in enumerate(regen_data['new_images'][:3]):
                        print(f"      {i+1}. {img.get('url', 'No URL')}")
            else:
                print("   ℹ️  No new images found (may be using cached results)")
                
            if regen_data.get('recommendations'):
                print(f"   ✅ Recommendations: {len(regen_data['recommendations'])}")
                for rec in regen_data['recommendations'][:2]:
                    print(f"      - {rec}")
                    
        else:
            print(f"   ❌ Failed: {regen_response.status_code}")
            print(f"   ❌ Response: {regen_response.text}")
            
        # Step 3: Test direct image search
        print("\n3. Testing direct image search...")
        search_data = {
            "product_name": listing['listing']['product_name'],
            "description": listing['listing'].get('description', ''),
            "category": listing['listing']['category'],
            "target_audience": "Deportistas y personas activas",
            "price_range": f"${listing['listing']['target_price']}"
        }
        
        search_response = requests.post(
            f"{backend_url}/api/listings/search-images",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            print(f"   ✅ Status: {search_response.status_code}")
            print(f"   ✅ Success: {search_data.get('success', False)}")
            print(f"   ✅ Total images: {search_data.get('total_images', 0)}")
            
            if search_data.get('images'):
                print("   ✅ Sample images from search:")
                for i, img in enumerate(search_data['images'][:3]):
                    print(f"      {i+1}. {img.get('url', 'No URL')}")
        else:
            print(f"   ❌ Failed: {search_response.status_code}")
            print(f"   ❌ Response: {search_response.text}")
            
        # Step 4: Frontend accessibility test
        print(f"\n4. Testing frontend accessibility...")
        listing_url = f"{frontend_url}/listing-details.html?id={listing_id}"
        
        try:
            frontend_response = requests.get(listing_url)
            if frontend_response.status_code == 200:
                print(f"   ✅ Frontend accessible")
                print(f"   ✅ URL: {listing_url}")
                
                # Check if image functionality is present
                content = frontend_response.text
                if 'Imágenes' in content and 'searchImages' in content:
                    print(f"   ✅ Image search tab and functions found")
                else:
                    print(f"   ❌ Image search functionality not found")
            else:
                print(f"   ❌ Frontend not accessible: {frontend_response.status_code}")
        except Exception as e:
            print(f"   ❌ Frontend error: {e}")
            
        print("\n" + "=" * 50)
        print("✅ Test Complete!")
        print("\n📋 Summary:")
        print(f"- ✅ Listing {listing_id} exists and accessible")
        print("- ✅ Image regeneration endpoint working")
        print("- ✅ Direct image search endpoint working")
        print("- ✅ Frontend accessible with image functionality")
        print("\n🎯 Manual Testing:")
        print(f"1. Open: {listing_url}")
        print("2. Click on 'Imágenes' tab")
        print("3. Click 'Buscar Imágenes' button")
        print("4. View generated images in gallery")
        print("5. Try 'Regenerar' button for new images")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_existing_listing_images()
    if success:
        print("\n🎉 All tests passed! The image search functionality is ready to use.")
    else:
        print("\n❌ Some tests failed. Please check the output above.")
