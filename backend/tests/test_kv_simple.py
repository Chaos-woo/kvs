import sys
import os
import json
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def test_create_kv_data():
    """Test the create_kv_data function directly"""
    print("[DEBUG_LOG] Testing create_kv_data function directly...")
    
    try:
        from models import SessionLocal
        from models.key_value import create_kv_data
        
        # Create a test session
        db = SessionLocal()
        
        # Test data
        key_text = "test_key_direct"
        val_list = ["test_value_1", "test_value_2"]
        
        print(f"[DEBUG_LOG] Creating KV with key: {key_text}, vals: {val_list}")
        
        # Test the function
        key = create_kv_data(db, key_text, val_list)
        db.commit()
        
        print(f"[DEBUG_LOG] Successfully created KV with ID: {key.id}")
        print(f"[DEBUG_LOG] Key: {key.key}")
        print(f"[DEBUG_LOG] Created at: {key.created_at}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {str(e)}")
        import traceback
        print(f"[DEBUG_LOG] Traceback: {traceback.format_exc()}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def test_database_setup():
    """Test if database and tables are set up correctly"""
    print("[DEBUG_LOG] Testing database setup...")
    
    try:
        from models import engine
        from models.key_value import create_fts5_table
        
        # Test database connection
        conn = engine.connect()
        print("[DEBUG_LOG] Database connection successful")
        
        # Test FTS5 table creation
        create_fts5_table()
        print("[DEBUG_LOG] FTS5 table creation successful")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"[DEBUG_LOG] Database setup error: {str(e)}")
        import traceback
        print(f"[DEBUG_LOG] Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("[DEBUG_LOG] Starting KV data tests...")
    
    # Test database setup first
    if test_database_setup():
        print("[DEBUG_LOG] Database setup test passed")
        
        # Test create_kv_data function
        if test_create_kv_data():
            print("[DEBUG_LOG] create_kv_data test passed")
        else:
            print("[DEBUG_LOG] create_kv_data test failed")
    else:
        print("[DEBUG_LOG] Database setup test failed")