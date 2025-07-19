import sys
import os
import tempfile
from unittest.mock import patch

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_production_mode():
    """Test production mode path configuration by simulating PyInstaller environment"""
    
    print("=== Production Mode Simulation Test ===")
    
    # Mock PyInstaller environment
    with patch.object(sys, 'frozen', True, create=True), \
         patch.object(sys, '_MEIPASS', '/fake/bundle/path', create=True), \
         patch.dict(os.environ, {'APPDATA': tempfile.gettempdir()}):
        
        # Reload the config module to pick up the mocked environment
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import is_development_mode, SQLITE_DB_PATH, LOG_DIR, DATA_DIR
        
        print(f"Development mode: {is_development_mode()}")
        print(f"Data directory: {DATA_DIR}")
        print(f"Database path: {SQLITE_DB_PATH}")
        print(f"Log directory: {LOG_DIR}")
        
        # Verify production mode behavior
        if not is_development_mode():
            print(f"\n✓ Production mode correctly detected")
            print(f"  - Database path contains temp dir: {tempfile.gettempdir() in SQLITE_DB_PATH}")
            print(f"  - Database path contains 'kvs': {'kvs' in SQLITE_DB_PATH}")
            print(f"  - Log directory contains temp dir: {tempfile.gettempdir() in LOG_DIR}")
            print(f"  - Log directory contains 'kvs': {'kvs' in LOG_DIR}")
        else:
            print(f"\n✗ Production mode detection failed")
        
        # Test directory creation
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            os.makedirs(LOG_DIR, exist_ok=True)
            print(f"\n✓ Directories can be created successfully")
            print(f"  - Data directory exists: {os.path.exists(DATA_DIR)}")
            print(f"  - Log directory exists: {os.path.exists(LOG_DIR)}")
        except Exception as e:
            print(f"\n✗ Directory creation failed: {e}")

if __name__ == "__main__":
    test_production_mode()