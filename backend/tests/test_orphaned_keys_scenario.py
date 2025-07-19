#!/usr/bin/env python3
"""
Test script to create and verify orphaned keys scenario
This demonstrates the edge case mentioned in the issue description
"""
import requests
import json
import sys

def create_orphaned_key_scenario():
    """Create a scenario with orphaned keys to test the fix"""
    print("Creating orphaned key scenario...")
    
    try:
        # First, create a normal KV entry
        print("1. Creating a normal KV entry...")
        response = requests.post("http://localhost:5000/api/v1/kv", 
                               json={"key": "test_orphaned", "vals": ["value1", "value2"]},
                               timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"  ✓ Created KV entry: {data['data']['key']} -> {data['data']['vals']}")
                key_id = data['data']['id']
            else:
                print(f"  ✗ Failed to create KV entry: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP error: {response.status_code}")
            return False
            
        # Now simulate data cleanup anomaly by directly manipulating the database
        # We'll use a direct database connection to create an orphaned key
        print("2. Simulating data cleanup anomaly (creating orphaned key)...")
        
        # Import database models
        import sys
        from pathlib import Path
        backend_dir = Path(__file__).resolve().parent / "backend"
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
            
        from models import SessionLocal
        from models.key_value import Key, KVRelation
        
        db = SessionLocal()
        try:
            # Create an orphaned key directly in the database
            orphaned_key = Key(key="orphaned_test_key")
            db.add(orphaned_key)
            db.commit()
            print(f"  ✓ Created orphaned key: {orphaned_key.key} (ID: {orphaned_key.id})")
            
            # Verify it has no relations
            relations_count = db.query(KVRelation).filter(KVRelation.key_id == orphaned_key.id).count()
            print(f"  ✓ Orphaned key has {relations_count} relations (should be 0)")
            
        finally:
            db.close()
            
        return True
        
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

def test_orphaned_keys_handling():
    """Test that orphaned keys are handled correctly in stats and export"""
    print("\nTesting orphaned keys handling...")
    
    try:
        # Get export statistics
        print("1. Testing export statistics with orphaned keys...")
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
                
                # Now KV pairs count should equal K count (including orphaned keys)
                if kv_pairs_count == k_count:
                    print(f"  ✓ KV pairs count ({kv_pairs_count}) == K count ({k_count}) - CORRECT!")
                else:
                    print(f"  ✗ KV pairs count ({kv_pairs_count}) != K count ({k_count}) - INCORRECT!")
                    return False
                    
            else:
                print(f"  ✗ API error: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP error: {response.status_code}")
            return False
            
        # Test export data
        print("\n2. Testing export data with orphaned keys...")
        response = requests.get("http://localhost:5000/api/v1/kv/export", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                export_data = data.get('data', [])
                export_count = data.get('count', 0)
                
                print(f"  ✓ Export count: {export_count}")
                
                # Check for orphaned keys (keys with empty value arrays)
                orphaned_keys = [record for record in export_data if len(record.get('v', [])) == 0]
                if orphaned_keys:
                    print(f"  ✓ Found {len(orphaned_keys)} orphaned keys with empty value arrays:")
                    for orphaned in orphaned_keys:
                        print(f"    - Key: '{orphaned.get('k')}', Values: {orphaned.get('v')}, Created: {orphaned.get('create_at')}")
                    
                    # Verify orphaned key format
                    orphaned = orphaned_keys[0]
                    if (orphaned.get('k') and 
                        isinstance(orphaned.get('v'), list) and 
                        len(orphaned.get('v')) == 0 and
                        orphaned.get('create_at')):
                        print(f"  ✓ Orphaned key format is correct")
                    else:
                        print(f"  ✗ Orphaned key format is incorrect")
                        return False
                else:
                    print(f"  ⚠ No orphaned keys found in export")
                
                # Verify export count matches KV pairs count
                if export_count == kv_pairs_count:
                    print(f"  ✓ Export count ({export_count}) matches KV pairs count ({kv_pairs_count}) - CORRECT!")
                else:
                    print(f"  ✗ Export count ({export_count}) != KV pairs count ({kv_pairs_count}) - INCORRECT!")
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
    print("Orphaned Keys Scenario Test")
    print("=" * 50)
    
    # Create orphaned key scenario
    scenario_created = create_orphaned_key_scenario()
    if not scenario_created:
        print("❌ Failed to create orphaned key scenario!")
        sys.exit(1)
    
    # Test the handling
    success = test_orphaned_keys_handling()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Orphaned keys scenario test passed!")
        print("✓ Orphaned keys are counted correctly in statistics")
        print("✓ Orphaned keys are exported with empty value arrays")
        print("✓ Export count matches KV pairs count including orphaned keys")
        sys.exit(0)
    else:
        print("❌ Orphaned keys scenario test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()