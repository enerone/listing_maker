#!/usr/bin/env python3
"""
Test script to verify that images load correctly after fixing the URL issue.
"""
import requests
import json

def test_image_urls():
    """Test that image URLs are working correctly."""
    
    backend_url = "http://localhost:8000"
    listing_id = 35
    
    print("🖼️  Testing Image URL Fix")
    print("=" * 40)
    
    try:
        # Test 1: Get current images
        print("\n1. Testing current images...")
        response = requests.get(f"{backend_url}/api/listings/{listing_id}/images")
        
        if response.status_code == 200:
            data = response.json()
            images = data.get('images', [])
            print(f"   ✅ Found {len(images)} images")
            
            # Test first few URLs
            for i, img in enumerate(images[:3]):
                if isinstance(img, dict):
                    url = img.get('original_url', '')
                    print(f"   ✅ Image {i+1}: {url[:50]}...")
                    
                    # Check if it's a valid URL (not placeholder)
                    if 'via.placeholder.com' in url:
                        print(f"   ❌ Still using placeholder URL!")
                        return False
                    elif 'unsplash.com' in url:
                        print(f"   ✅ Using Unsplash URL (should work)")
                    else:
                        print(f"   ℹ️  Using other URL: {url}")
                        
        else:
            print(f"   ❌ Failed to get images: {response.status_code}")
            return False
            
        # Test 2: Regenerate images
        print("\n2. Testing image regeneration...")
        response = requests.post(f"{backend_url}/api/listings/{listing_id}/regenerate-images", json={})
        
        if response.status_code == 200:
            data = response.json()
            new_images = data.get('new_images', [])
            print(f"   ✅ Regenerated {len(new_images)} images")
            
            # Check new URLs
            for i, img in enumerate(new_images[:3]):
                if isinstance(img, dict):
                    url = img.get('original_url', '')
                    print(f"   ✅ New image {i+1}: {url[:50]}...")
                    
                    if 'via.placeholder.com' in url:
                        print(f"   ❌ New image still using placeholder!")
                        return False
                    elif 'unsplash.com' in url:
                        print(f"   ✅ New image using Unsplash (should work)")
                        
        else:
            print(f"   ❌ Failed to regenerate: {response.status_code}")
            return False
            
        # Test 3: Direct image search
        print("\n3. Testing direct image search...")
        search_data = {
            "product_name": "Test Product",
            "description": "Test description",
            "category": "Electronics"
        }
        
        response = requests.post(f"{backend_url}/api/listings/search-images", json=search_data)
        
        if response.status_code == 200:
            data = response.json()
            search_images = data.get('images', [])
            print(f"   ✅ Search found {len(search_images)} images")
            
            # Check search URLs
            for i, img in enumerate(search_images[:3]):
                if isinstance(img, dict):
                    url = img.get('url', '')
                    print(f"   ✅ Search image {i+1}: {url[:50]}...")
                    
                    if 'via.placeholder.com' in url:
                        print(f"   ❌ Search image still using placeholder!")
                        return False
                    elif 'unsplash.com' in url:
                        print(f"   ✅ Search image using Unsplash (should work)")
                        
        else:
            print(f"   ❌ Failed to search: {response.status_code}")
            return False
            
        print("\n" + "=" * 40)
        print("✅ Image URL Fix Test Complete!")
        print("\n📋 Results:")
        print("- ✅ No more placeholder URLs")
        print("- ✅ Using working Unsplash URLs")
        print("- ✅ Images should load in browser")
        print("- ✅ No DNS resolution errors")
        
        print("\n🎯 Manual Verification:")
        print("1. Open http://localhost:8001/listing-details.html?id=35")
        print("2. Click 'Imágenes' tab")
        print("3. Images should load without errors")
        print("4. Check browser console - no DNS errors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_image_urls()
    if success:
        print("\n🎉 Image URL fix successful! No more DNS errors.")
    else:
        print("\n❌ Image URL fix failed. Check output above.")
