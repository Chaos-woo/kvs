#!/usr/bin/env python3
"""
Test script to verify the search mode functionality
"""

import requests
import json

# Test configuration
BASE_URL = "http://127.0.0.1:5000/api/v1"
TEST_QUERY = "test"

def test_search_modes():
    """Test all three search modes"""
    
    print("Testing KV Search Mode Functionality")
    print("=" * 50)
    
    # Test modes
    modes = [
        ("key", "K搜索 - Key search only"),
        ("value", "V搜索 - Value search only"), 
        ("mixed", "KV混合搜索 - Mixed search (default)")
    ]
    
    for mode, description in modes:
        print(f"\n🔍 Testing {description}")
        print(f"Mode: {mode}")
        
        try:
            # Make API request
            url = f"{BASE_URL}/kv/search"
            params = {
                "q": TEST_QUERY,
                "mode": mode
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    results_count = len(data.get("data", []))
                    print(f"✅ Success: Found {results_count} results")
                    
                    # Show first result if available
                    if results_count > 0:
                        first_result = data["data"][0]
                        print(f"   Sample result: Key='{first_result.get('key')}', Vals={first_result.get('vals')}")
                else:
                    print(f"❌ API Error: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
            print("   Make sure the backend server is running with: python app.py")
    
    print(f"\n{'=' * 50}")
    print("Test completed!")
    print("\nTo run the full application:")
    print("1. Backend: python app.py")
    print("2. Frontend: npm run tauri dev (in frontend directory)")

if __name__ == "__main__":
    test_search_modes()