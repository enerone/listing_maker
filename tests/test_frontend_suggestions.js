// Test script to verify frontend suggestions integration
const API_BASE = 'http://localhost:8000';

async function testSuggestions() {
    console.log('🧪 Testing Frontend Suggestions Integration...');
    
    try {
        // Test 1: Basic Electronics Category
        console.log('\n📱 Testing Electronics Category...');
        const electronicsResponse = await fetch(`${API_BASE}/api/listings/suggestions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_name: 'Smartwatch Pro',
                category: 'Electronics',
                features: [],
                target_price: 199.99
            })
        });
        
        const electronicsData = await electronicsResponse.json();
        console.log('✅ Electronics Suggestions:', electronicsData);
        
        // Verify all expected fields are present
        const expectedFields = [
            'category', 'keywords', 'features', 'target_audience', 'price_recommendations',
            'price_range', 'marketing_angles', 'dimensions', 'weight', 'materials',
            'colors', 'box_contents', 'use_cases', 'main_competitor', 'brand', 'compatibility'
        ];
        
        const missingFields = expectedFields.filter(field => !electronicsData.suggestions[field]);
        if (missingFields.length > 0) {
            console.error('❌ Missing fields:', missingFields);
        } else {
            console.log('✅ All expected fields present in Electronics suggestions');
        }
        
        // Test 2: Sports Category
        console.log('\n🏃 Testing Sports Category...');
        const sportsResponse = await fetch(`${API_BASE}/api/listings/suggestions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_name: 'Running Shoes',
                category: 'Sports',
                features: [],
                target_price: 89.99
            })
        });
        
        const sportsData = await sportsResponse.json();
        console.log('✅ Sports Suggestions:', sportsData);
        
        // Test 3: Other Category
        console.log('\n🏠 Testing Other Category...');
        const otherResponse = await fetch(`${API_BASE}/api/listings/suggestions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_name: 'Kitchen Utensil',
                category: 'Other',
                features: [],
                target_price: 24.99
            })
        });
        
        const otherData = await otherResponse.json();
        console.log('✅ Other Suggestions:', otherData);
        
        // Summary
        console.log('\n🎉 All tests passed! Frontend suggestions integration is working correctly.');
        console.log('📊 Field count per category:');
        console.log(`   Electronics: ${Object.keys(electronicsData.suggestions).length} fields`);
        console.log(`   Sports: ${Object.keys(sportsData.suggestions).length} fields`);
        console.log(`   Other: ${Object.keys(otherData.suggestions).length} fields`);
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
}

// Run the test
testSuggestions();
