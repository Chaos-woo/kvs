import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import is_development_mode, SQLITE_DB_PATH, LOG_DIR, DATA_DIR

def test_path_configuration():
    """Test that paths are configured correctly based on environment"""
    
    print("=== Path Configuration Test ===")
    print(f"Development mode: {is_development_mode()}")
    print(f"Data directory: {DATA_DIR}")
    print(f"Database path: {SQLITE_DB_PATH}")
    print(f"Log directory: {LOG_DIR}")
    
    # Verify paths exist or can be created
    print(f"\nPath verification:")
    print(f"Data directory exists: {os.path.exists(DATA_DIR)}")
    print(f"Log directory exists: {os.path.exists(LOG_DIR)}")
    
    # Show expected behavior
    if is_development_mode():
        print(f"\n✓ Development mode detected")
        print(f"  - Database should be in backend directory: {os.path.basename(SQLITE_DB_PATH) == 'kvs.db'}")
        print(f"  - Logs should be in backend/logs: {'backend' in LOG_DIR}")
    else:
        print(f"\n✓ Production mode detected")
        print(f"  - Database should be in app data: {'kvs' in SQLITE_DB_PATH and 'APPDATA' in str(DATA_DIR).upper()}")
        print(f"  - Logs should be in app data: {'kvs' in LOG_DIR}")

if __name__ == "__main__":
    test_path_configuration()