#!/usr/bin/env python3
"""
Test script to verify that database tables are created correctly.
This script tests the fix for the issue where kvs.db tables were not being created in packaged version.
"""

import os
import sys
from pathlib import Path
import sqlite3

# Add the current directory to the Python path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def test_database_creation():
    """Test that database tables are created correctly"""
    print("[DEBUG_LOG] Starting database creation test...")
    
    try:
        # Import the models and database setup
        from models import Base, engine
        from models.key_value import Key, Val, KVRelation, create_fts5_table
        from config import SQLITE_DB_PATH
        
        print(f"[DEBUG_LOG] Database path: {SQLITE_DB_PATH}")
        
        # Remove existing database file if it exists
        if os.path.exists(SQLITE_DB_PATH):
            os.remove(SQLITE_DB_PATH)
            print("[DEBUG_LOG] Removed existing database file")
        
        # Create all tables
        print("[DEBUG_LOG] Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create FTS5 table
        print("[DEBUG_LOG] Creating FTS5 table...")
        create_fts5_table()
        
        # Verify tables exist
        print("[DEBUG_LOG] Verifying tables exist...")
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"[DEBUG_LOG] Found tables: {tables}")
        
        # Check for required tables
        required_tables = ['keys', 'vals', 'kv_relations', 'kv_search']
        missing_tables = []
        
        for table in required_tables:
            if table not in tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"[ERROR] Missing tables: {missing_tables}")
            return False
        else:
            print("[SUCCESS] All required tables created successfully!")
            
            # Show table schemas
            for table in required_tables:
                if table != 'kv_search':  # Skip FTS5 virtual table
                    cursor.execute(f"PRAGMA table_info({table});")
                    columns = cursor.fetchall()
                    print(f"[DEBUG_LOG] Table '{table}' columns: {[col[1] for col in columns]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Database creation test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_creation()
    if success:
        print("\n✅ Database creation test PASSED")
        sys.exit(0)
    else:
        print("\n❌ Database creation test FAILED")
        sys.exit(1)