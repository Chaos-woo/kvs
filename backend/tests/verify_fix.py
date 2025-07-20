#!/usr/bin/env python3
"""
Simple verification script to test the database table creation fix.
This verifies that the models can be imported correctly and tables are created.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def verify_imports():
    """Verify that all models can be imported correctly"""
    print("[DEBUG_LOG] Testing model imports...")
    
    try:
        # Test importing Base and engine
        from models import Base, engine
        print("[SUCCESS] Successfully imported Base and engine from models")
        
        # Test importing model classes
        from models.key_value import Key, Val, KVRelation, create_fts5_table
        print("[SUCCESS] Successfully imported Key, Val, KVRelation from models.key_value")
        
        # Verify that models are registered with Base
        tables = Base.metadata.tables
        print(f"[DEBUG_LOG] Registered tables: {list(tables.keys())}")
        
        expected_tables = ['keys', 'vals', 'kv_relations']
        missing_tables = []
        
        for table in expected_tables:
            if table not in tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"[ERROR] Missing table definitions: {missing_tables}")
            return False
        else:
            print("[SUCCESS] All expected tables are registered with Base")
            return True
            
    except Exception as e:
        print(f"[ERROR] Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_table_creation():
    """Verify that tables can be created successfully"""
    print("\n[DEBUG_LOG] Testing table creation...")
    
    try:
        from models import Base, engine
        from models.key_value import create_fts5_table
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Successfully created all tables")
        
        # Create FTS5 table
        create_fts5_table()
        print("[SUCCESS] Successfully created FTS5 table")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Table creation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification tests"""
    print("=== Database Table Creation Fix Verification ===\n")
    
    # Test 1: Import verification
    import_success = verify_imports()
    
    # Test 2: Table creation verification
    table_success = verify_table_creation()
    
    # Summary
    print("\n=== Verification Summary ===")
    if import_success and table_success:
        print("✅ All verification tests PASSED")
        print("✅ The database table creation fix is working correctly")
        return True
    else:
        print("❌ Some verification tests FAILED")
        print("❌ The fix needs additional work")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)