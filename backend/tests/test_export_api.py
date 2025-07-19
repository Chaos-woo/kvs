#!/usr/bin/env python3
"""
Test script for KV export API endpoints
"""
import requests
import json
import sys

def test_export_stats():
    """Test the export statistics endpoint"""
    try:
        print("Testing export statistics endpoint...")
        response = requests.get("http://localhost:5000/api/v1/kv/export/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Export stats endpoint working")
            print(f"  Status: {data.get('status')}")
            if data.get('status') == 'success':
                stats = data.get('data', {})
                print(f"  K count: {stats.get('k_count')}")
                print(f"  V count: {stats.get('v_count')}")
                print(f"  KV pairs count: {stats.get('kv_pairs_count')}")
            return True
        else:
            print(f"✗ Export stats endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Export stats endpoint error: {e}")
        return False

def test_export_data():
    """Test the export data endpoint"""
    try:
        print("\nTesting export data endpoint...")
        response = requests.get("http://localhost:5000/api/v1/kv/export", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Export data endpoint working")
            print(f"  Status: {data.get('status')}")
            if data.get('status') == 'success':
                export_data = data.get('data', [])
                count = data.get('count', 0)
                print(f"  Export count: {count}")
                
                # Check format of first record if available
                if export_data:
                    first_record = export_data[0]
                    print(f"  Sample record format:")
                    print(f"    k: {first_record.get('k')}")
                    print(f"    v: {first_record.get('v')}")
                    print(f"    create_at: {first_record.get('create_at')}")
                    
                    # Verify JSONL format
                    jsonl_line = json.dumps(first_record)
                    print(f"  JSONL format: {jsonl_line}")
                    
            return True
        else:
            print(f"✗ Export data endpoint failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Export data endpoint error: {e}")
        return False

def main():
    """Main test function"""
    print("KV Export API Test")
    print("=" * 50)
    
    # Test both endpoints
    stats_ok = test_export_stats()
    data_ok = test_export_data()
    
    print("\n" + "=" * 50)
    if stats_ok and data_ok:
        print("✓ All export API tests passed!")
        sys.exit(0)
    else:
        print("✗ Some export API tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()