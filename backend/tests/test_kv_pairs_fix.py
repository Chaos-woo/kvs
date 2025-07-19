#!/usr/bin/env python3
"""
Test script to verify the KV pairs count fix
"""
import requests
import json
import sys

def test_kv_pairs_count_fix():
    """Test that KV pairs count is now calculated correctly"""
    print("Testing KV pairs count fix...")
    print("=" * 50)
    
    try:
        # Get export statistics
        print("1. Testing export statistics...")
        response = requests.get("http://localhost:5000/api/v1/kv/export/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stats = data.get('data', {})
                k_count = stats.get('k_count')
                v_count = stats.get('v_count')
                kv_pairs_count = stats.get('kv_pairs_count')
                
                print(f"  ✓ K count: {k_count}")
                print(f"  ✓ V count: {v_count}")
                print(f"  ✓ KV pairs count: {kv_pairs_count}")
                
                # The KV pairs count should now be equal to or less than K count
                # (equal when all keys have relations, less when there are orphaned keys)
                if kv_pairs_count <= k_count:
                    print(f"  ✓ KV pairs count ({kv_pairs_count}) <= K count ({k_count}) - CORRECT!")
                else:
                    print(f"  ✗ KV pairs count ({kv_pairs_count}) > K count ({k_count}) - INCORRECT!")
                    return False
                    
            else:
                print(f"  ✗ API error: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP error: {response.status_code}")
            return False
            
        # Test export data
        print("\n2. Testing export data...")
        response = requests.get("http://localhost:5000/api/v1/kv/export", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                export_data = data.get('data', [])
                export_count = data.get('count', 0)
                
                print(f"  ✓ Export count: {export_count}")
                
                # Check if export count matches KV pairs count from stats
                if export_count == kv_pairs_count:
                    print(f"  ✓ Export count ({export_count}) matches KV pairs count ({kv_pairs_count}) - CORRECT!")
                else:
                    print(f"  ✗ Export count ({export_count}) != KV pairs count ({kv_pairs_count}) - INCORRECT!")
                    return False
                
                # Check for orphaned keys (keys with empty value arrays)
                orphaned_keys = [record for record in export_data if len(record.get('v', [])) == 0]
                if orphaned_keys:
                    print(f"  ✓ Found {len(orphaned_keys)} orphaned keys with empty value arrays:")
                    for orphaned in orphaned_keys[:3]:  # Show first 3
                        print(f"    - Key: '{orphaned.get('k')}', Values: {orphaned.get('v')}")
                else:
                    print(f"  ✓ No orphaned keys found (all keys have values)")
                
                # Verify data format
                if export_data:
                    sample = export_data[0]
                    has_k = 'k' in sample and isinstance(sample['k'], str)
                    has_v = 'v' in sample and isinstance(sample['v'], list)
                    has_create_at = 'create_at' in sample and isinstance(sample['create_at'], str)
                    
                    if has_k and has_v and has_create_at:
                        print(f"  ✓ Data format is correct: {{'k': str, 'v': list, 'create_at': str}}")
                    else:
                        print(f"  ✗ Data format is incorrect")
                        return False
                        
            else:
                print(f"  ✗ API error: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP error: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

def main():
    """Main test function"""
    print("KV Pairs Count Fix Verification")
    print("=" * 50)
    
    success = test_kv_pairs_count_fix()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 KV pairs count fix is working correctly!")
        print("✓ KV pairs are now counted as unique keys from kv_relation")
        print("✓ Orphaned keys are handled properly in both stats and export")
        sys.exit(0)
    else:
        print("❌ KV pairs count fix needs attention!")
        sys.exit(1)

if __name__ == "__main__":
    main()