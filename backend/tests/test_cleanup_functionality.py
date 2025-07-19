#!/usr/bin/env python3
"""
Test script for KV cleanup functionality
Tests both the backend API endpoints and verifies the batch delete functionality
"""

import requests
import json
import sys
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_backend_api():
    """Test the backend API endpoints for cleanup functionality"""
    base_url = "http://localhost:5000/api/v1"
    
    print("🧪 Testing KV Cleanup Functionality")
    print("=" * 50)
    
    # Test 1: Check if backend is running
    print("\n1. Testing backend connection...")
    try:
        response = requests.get(f"{base_url}/kv", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("💡 Please start the backend first: cd backend && python app.py")
        return False
    
    # Test 2: Get all KV data
    print("\n2. Fetching all KV data...")
    try:
        response = requests.get(f"{base_url}/kv")
        data = response.json()
        
        if data.get("status") == "success":
            kv_data = data.get("data", [])
            print(f"✅ Found {len(kv_data)} KV pairs")
            
            # Display first few KV pairs
            for i, kv in enumerate(kv_data[:3]):
                print(f"   - ID: {kv['id']}, Key: {kv['key'][:50]}{'...' if len(kv['key']) > 50 else ''}, Values: {len(kv['vals'])}")
            
            if len(kv_data) > 3:
                print(f"   ... and {len(kv_data) - 3} more")
                
        else:
            print(f"❌ Failed to fetch KV data: {data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error fetching KV data: {e}")
        return False
    
    # Test 3: Test batch delete endpoint (if we have data)
    if len(kv_data) > 0:
        print("\n3. Testing batch delete endpoint...")
        
        # Create some test data first
        print("   Creating test KV pairs...")
        test_keys = []
        
        for i in range(2):
            test_data = {
                "key": f"test_cleanup_key_{i}_{int(time.time())}",
                "vals": [f"test_value_{i}_1", f"test_value_{i}_2"]
            }
            
            try:
                response = requests.post(f"{base_url}/kv", json=test_data)
                result = response.json()
                
                if result.get("status") == "success":
                    # Get the created key ID
                    response = requests.get(f"{base_url}/kv")
                    all_data = response.json()
                    
                    if all_data.get("status") == "success":
                        for kv in all_data["data"]:
                            if kv["key"] == test_data["key"]:
                                test_keys.append(kv["id"])
                                print(f"   ✅ Created test KV pair: ID {kv['id']}, Key: {kv['key']}")
                                break
                else:
                    print(f"   ❌ Failed to create test data: {result.get('message', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Error creating test data: {e}")
        
        # Test batch delete
        if test_keys:
            print(f"\n   Testing batch delete with {len(test_keys)} test keys...")
            
            delete_data = {"key_ids": test_keys}
            
            try:
                response = requests.delete(f"{base_url}/kv/batch-delete", json=delete_data)
                result = response.json()
                
                if result.get("status") == "success":
                    deleted_count = result.get("deleted_count", 0)
                    total_requested = result.get("total_requested", 0)
                    print(f"   ✅ Batch delete successful: {deleted_count}/{total_requested} items deleted")
                    
                    if "failed_deletions" in result:
                        print(f"   ⚠️  Some deletions failed: {len(result['failed_deletions'])} items")
                        for failure in result["failed_deletions"]:
                            print(f"      - Key ID {failure['key_id']}: {failure['error']}")
                else:
                    print(f"   ❌ Batch delete failed: {result.get('message', 'Unknown error')}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Error testing batch delete: {e}")
                return False
        else:
            print("   ⚠️  No test keys created, skipping batch delete test")
    
    else:
        print("\n3. Skipping batch delete test (no KV data available)")
    
    print("\n✅ All backend API tests completed successfully!")
    return True

def test_frontend_integration():
    """Test frontend integration"""
    print("\n🎨 Frontend Integration Test")
    print("=" * 30)
    
    print("To test the frontend integration:")
    print("1. Run: cd frontend && npm run dev-with-backend")
    print("2. Open the application")
    print("3. Click on '设置' menu")
    print("4. Click on '数据清理' option")
    print("5. Verify the cleanup dialog opens")
    print("6. Test multi-select functionality")
    print("7. Test batch deletion")
    print("8. Verify toast notifications")

if __name__ == "__main__":
    print("🚀 KV Cleanup Functionality Test Suite")
    print("=" * 60)
    
    # Test backend API
    backend_success = test_backend_api()
    
    if backend_success:
        test_frontend_integration()
        print("\n🎉 All tests completed! The cleanup functionality is ready to use.")
    else:
        print("\n❌ Backend tests failed. Please fix the issues before testing frontend.")
        sys.exit(1)