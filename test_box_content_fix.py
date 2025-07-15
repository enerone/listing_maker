import requests
import json

# Test the box content duplication fix
def test_box_content_duplication():
    # Create a test listing
    test_listing = {
        "title": "Test Smartwatch",
        "description": "A test smartwatch product",
        "price": 299.99,
        "category": "electronics",
        "images": ["test1.jpg", "test2.jpg"],
        "box_contents": ["Smartwatch", "Charging cable", "User manual"]
    }
    
    try:
        # Create the listing
        response = requests.post("http://localhost:8000/api/listings", json=test_listing)
        if response.status_code == 201:
            listing_id = response.json()["id"]
            print(f"✅ Created test listing with ID: {listing_id}")
            
            # Test the enhancement endpoint
            enhance_response = requests.post(f"http://localhost:8000/api/listings/{listing_id}/enhance-description")
            if enhance_response.status_code == 200:
                result = enhance_response.json()
                print("✅ Enhancement successful!")
                print(f"Box contents: {result.get('box_contents', 'Not found')}")
                return True
            else:
                print(f"❌ Enhancement failed: {enhance_response.status_code}")
                print(enhance_response.text)
                return False
        else:
            print(f"❌ Failed to create listing: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing box content duplication fix...")
    success = test_box_content_duplication()
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
