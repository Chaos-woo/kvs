#!/usr/bin/env python3
"""
Test script to verify FTS5 virtual table data handling for KV operations.

This script tests the four operations mentioned in the issue:
1. 单独创建KV (Single KV creation): Check if FTS5 virtual table data is added
2. 单独删除KV (Single KV deletion): Check if FTS5 virtual table data is deleted  
3. 数据导入KV (KV data import): Check if FTS5 virtual table data is added
4. 数据清理KV (KV data cleanup): Check if FTS5 virtual table data is deleted
"""

import sys
import os
import requests
import json
import time
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import database models
try:
    from models import SessionLocal
    from sqlalchemy import text
except ImportError as e:
    print(f"Import error: {e}")
    print("Please make sure the backend directory is accessible and models are properly configured.")
    sys.exit(1)

def check_fts5_data(db_session, key_id=None, expected_count=None):
    """Check FTS5 virtual table data"""
    try:
        if key_id:
            result = db_session.execute(text("SELECT COUNT(*) FROM kv_search WHERE key_id = :key_id"), {"key_id": key_id})
            count = result.scalar()
            print(f"[DEBUG_LOG] FTS5 entries for key_id {key_id}: {count}")
            return count
        else:
            result = db_session.execute(text("SELECT COUNT(*) FROM kv_search"))
            count = result.scalar()
            print(f"[DEBUG_LOG] Total FTS5 entries: {count}")
            return count
    except Exception as e:
        print(f"[DEBUG_LOG] Error checking FTS5 data: {e}")
        return -1

def test_single_kv_creation():
    """Test 1: 单独创建KV - Check if FTS5 virtual table data is added"""
    print("\n=== Test 1: Single KV Creation ===")
    
    # Create a new KV entry
    test_data = {
        "key": "test_key_creation",
        "vals": ["value1", "value2", "value3"]
    }
    
    try:
        response = requests.post("http://localhost:5000/api/kv", json=test_data)
        print(f"[DEBUG_LOG] Create KV response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            key_id = data["data"]["id"]
            print(f"[DEBUG_LOG] Created KV with ID: {key_id}")
            
            # Check FTS5 data
            db = SessionLocal()
            try:
                fts5_count = check_fts5_data(db, key_id)
                if fts5_count == 1:
                    print("✓ Test 1 PASSED: FTS5 data correctly added for single KV creation")
                    return key_id
                else:
                    print(f"✗ Test 1 FAILED: Expected 1 FTS5 entry, found {fts5_count}")
                    return None
            finally:
                db.close()
        else:
            print(f"✗ Test 1 FAILED: HTTP {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Test 1 FAILED: {e}")
        return None

def test_single_kv_deletion(key_id):
    """Test 2: 单独删除KV - Check if FTS5 virtual table data is deleted"""
    print("\n=== Test 2: Single KV Deletion ===")
    
    if not key_id:
        print("✗ Test 2 SKIPPED: No key_id from previous test")
        return False
    
    try:
        # Delete the KV entry
        response = requests.delete(f"http://localhost:5000/api/kv/{key_id}")
        print(f"[DEBUG_LOG] Delete KV response: {response.status_code}")
        
        if response.status_code == 200:
            # Check FTS5 data
            db = SessionLocal()
            try:
                fts5_count = check_fts5_data(db, key_id)
                if fts5_count == 0:
                    print("✓ Test 2 PASSED: FTS5 data correctly deleted for single KV deletion")
                    return True
                else:
                    print(f"✗ Test 2 FAILED: Expected 0 FTS5 entries, found {fts5_count}")
                    return False
            finally:
                db.close()
        else:
            print(f"✗ Test 2 FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        return False

def test_data_import():
    """Test 3: 数据导入KV - Check if FTS5 virtual table data is added"""
    print("\n=== Test 3: Data Import ===")
    
    # Import test data
    import_data = {
        "data": [
            {
                "k": "import_key_1",
                "v": ["import_val_1", "import_val_2"],
                "create_at": "2024-01-01T00:00:00Z"
            },
            {
                "k": "import_key_2", 
                "v": ["import_val_3", "import_val_4"],
                "create_at": "2024-01-01T00:00:00Z"
            }
        ]
    }
    
    try:
        # Get initial FTS5 count
        db = SessionLocal()
        initial_count = check_fts5_data(db)
        db.close()
        
        response = requests.post("http://localhost:5000/api/kv/import", json=import_data)
        print(f"[DEBUG_LOG] Import KV response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            imported_count = data.get("imported_count", 0)
            print(f"[DEBUG_LOG] Imported {imported_count} entries")
            
            # Check FTS5 data
            db = SessionLocal()
            try:
                final_count = check_fts5_data(db)
                expected_count = initial_count + imported_count
                
                if final_count == expected_count:
                    print("✓ Test 3 PASSED: FTS5 data correctly added for data import")
                    return True
                else:
                    print(f"✗ Test 3 FAILED: Expected {expected_count} FTS5 entries, found {final_count}")
                    return False
            finally:
                db.close()
        else:
            print(f"✗ Test 3 FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        return False

def test_data_cleanup():
    """Test 4: 数据清理KV - Check if FTS5 virtual table data is deleted"""
    print("\n=== Test 4: Data Cleanup (Batch Delete) ===")
    
    try:
        # Get all KV entries to find ones we can delete
        response = requests.get("http://localhost:5000/api/kv")
        if response.status_code != 200:
            print(f"✗ Test 4 FAILED: Could not get KV list - HTTP {response.status_code}")
            return False
            
        kv_data = response.json()
        if not kv_data.get("data"):
            print("✗ Test 4 SKIPPED: No KV entries to delete")
            return True
            
        # Get key IDs for entries we created in the import test
        key_ids_to_delete = []
        for item in kv_data["data"]:
            if item["key"].startswith("import_key_"):
                key_ids_to_delete.append(item["id"])
        
        if not key_ids_to_delete:
            print("✗ Test 4 SKIPPED: No import test entries found to delete")
            return True
            
        print(f"[DEBUG_LOG] Found {len(key_ids_to_delete)} entries to delete: {key_ids_to_delete}")
        
        # Get initial FTS5 count
        db = SessionLocal()
        initial_count = check_fts5_data(db)
        db.close()
        
        # Batch delete
        delete_data = {"key_ids": key_ids_to_delete}
        response = requests.delete("http://localhost:5000/api/kv/batch-delete", json=delete_data)
        print(f"[DEBUG_LOG] Batch delete response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            deleted_count = data.get("deleted_count", 0)
            print(f"[DEBUG_LOG] Deleted {deleted_count} entries")
            
            # Check FTS5 data
            db = SessionLocal()
            try:
                final_count = check_fts5_data(db)
                expected_count = initial_count - deleted_count
                
                if final_count == expected_count:
                    print("✓ Test 4 PASSED: FTS5 data correctly deleted for data cleanup")
                    return True
                else:
                    print(f"✗ Test 4 FAILED: Expected {expected_count} FTS5 entries, found {final_count}")
                    return False
            finally:
                db.close()
        else:
            print(f"✗ Test 4 FAILED: HTTP {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
        return False

def main():
    """Run all FTS5 operation tests"""
    print("Starting FTS5 Virtual Table Data Handling Tests")
    print("=" * 50)
    
    # Wait for backend to be ready
    print("Waiting for backend to be ready...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:5000/api/kv/stats")
            if response.status_code == 200:
                print("Backend is ready!")
                break
        except:
            pass
        time.sleep(1)
    else:
        print("✗ Backend is not responding. Please start the backend server first.")
        return
    
    # Run tests
    results = []
    
    # Test 1: Single KV Creation
    key_id = test_single_kv_creation()
    results.append(key_id is not None)
    
    # Test 2: Single KV Deletion
    result = test_single_kv_deletion(key_id)
    results.append(result)
    
    # Test 3: Data Import
    result = test_data_import()
    results.append(result)
    
    # Test 4: Data Cleanup
    result = test_data_cleanup()
    results.append(result)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    test_names = [
        "Single KV Creation (FTS5 Insert)",
        "Single KV Deletion (FTS5 Delete)", 
        "Data Import (FTS5 Insert)",
        "Data Cleanup (FTS5 Delete)"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"Test {i+1}: {name} - {status}")
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All FTS5 operations are working correctly!")
    else:
        print("⚠️  Some FTS5 operations need attention.")

if __name__ == "__main__":
    main()