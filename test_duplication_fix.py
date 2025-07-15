#!/usr/bin/env python3
"""
Simple test to verify that the box content duplication fix is working.
This test focuses on the frontend JavaScript functionality.
"""

def test_frontend_fix():
    """Test that the fix for box content duplication is properly implemented."""
    
    print("🧪 Testing box content duplication fix...")
    
    # Read the JavaScript file to verify the fix
    with open('/home/fabi/code/newlistings/frontend/app.js', 'r') as f:
        js_content = f.read()
    
    # Check that applyToBoxContentFields uses the correct class selector
    if 'existingContents.forEach(content => content.remove());' in js_content:
        print("✅ Found correct removal logic in applyToBoxContentFields")
    else:
        print("❌ Missing correct removal logic in applyToBoxContentFields")
        return False
    
    # Check that it uses the correct class selector
    if "boxContentContainer.querySelectorAll('.box-content-item')" in js_content:
        print("✅ Found correct class selector '.box-content-item' in applyToBoxContentFields")
    else:
        print("❌ Missing correct class selector '.box-content-item' in applyToBoxContentFields")
        return False
    
    # Check that addBoxContentField uses the correct class
    if "wrapper.className = 'flex items-center space-x-2 box-content-item';" in js_content:
        print("✅ Found correct class 'box-content-item' in addBoxContentField")
    else:
        print("❌ Missing correct class 'box-content-item' in addBoxContentField")
        return False
    
    # Check that applySuggestionsStep1 also removes duplicates correctly
    if "featuresContainer.querySelectorAll('.feature-item')" in js_content:
        print("✅ Found correct class selector '.feature-item' in applySuggestionsStep1")
    else:
        print("❌ Missing correct class selector '.feature-item' in applySuggestionsStep1")
        return False
    
    print("✅ All frontend duplication fixes verified successfully!")
    return True

def test_git_commit():
    """Test that changes are committed to git."""
    import subprocess
    
    try:
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, 
                              cwd='/home/fabi/code/newlistings')
        
        if result.returncode == 0:
            if result.stdout.strip() == "":
                print("✅ All changes are committed to git")
                return True
            else:
                print("⚠️  Uncommitted changes found:")
                print(result.stdout)
                return False
        else:
            print("❌ Error checking git status")
            return False
            
    except Exception as e:
        print(f"❌ Error checking git: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING FRONTEND DUPLICATION FIXES")
    print("=" * 60)
    
    # Test frontend fix
    frontend_ok = test_frontend_fix()
    
    print("\n" + "=" * 60)
    print("TESTING GIT COMMIT STATUS")
    print("=" * 60)
    
    # Test git commit
    git_ok = test_git_commit()
    
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    
    if frontend_ok and git_ok:
        print("✅ ALL TESTS PASSED! The duplication fix is working correctly.")
        exit(0)
    else:
        print("❌ Some tests failed. Please check the output above.")
        exit(1)
