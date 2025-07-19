import os
import sys
import time
import requests
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_dir))

from config import is_development_mode, LOG_DIR, API_LOG_FILE, ERROR_LOG_FILE, FRONTEND_LOG_FILE

def test_logging_paths():
    """Test that logging paths are correctly configured"""
    print("=== Logging Path Configuration Test ===")
    
    is_dev = is_development_mode()
    print(f"Environment: {'Development' if is_dev else 'Production'}")
    print(f"Log Directory: {LOG_DIR}")
    print(f"API Log File: {API_LOG_FILE}")
    print(f"Error Log File: {ERROR_LOG_FILE}")
    print(f"Frontend Log File: {FRONTEND_LOG_FILE}")
    
    # Check if log directory exists
    if os.path.exists(LOG_DIR):
        print(f"✓ Log directory exists: {LOG_DIR}")
        
        # List files in log directory
        log_files = os.listdir(LOG_DIR)
        print(f"Files in log directory: {log_files}")
        
        # Check each log file
        for log_file, log_path in [
            ("api.log", API_LOG_FILE),
            ("error.log", ERROR_LOG_FILE), 
            ("frontend.log", FRONTEND_LOG_FILE)
        ]:
            if os.path.exists(log_path):
                size = os.path.getsize(log_path)
                print(f"✓ {log_file} exists ({size} bytes)")
            else:
                print(f"✗ {log_file} does not exist")
    else:
        print(f"✗ Log directory does not exist: {LOG_DIR}")
        # Create it
        os.makedirs(LOG_DIR, exist_ok=True)
        print(f"✓ Created log directory: {LOG_DIR}")

def test_backend_logging():
    """Test backend logging by making API requests"""
    print("\n=== Backend Logging Test ===")
    
    try:
        # Test API endpoint
        response = requests.get('http://localhost:5000/api/v1/health', timeout=5)
        print(f"✓ API request successful: {response.status_code}")
        
        # Wait a moment for logs to be written
        time.sleep(1)
        
        # Check if API log was written
        if os.path.exists(API_LOG_FILE):
            with open(API_LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"✓ API log has {len(lines)} lines")
                    print(f"Last log entry: {lines[-1].strip()}")
                else:
                    print("✗ API log file is empty")
        else:
            print("✗ API log file not found")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Could not connect to backend: {e}")
        print("Make sure the Flask backend is running on localhost:5000")

if __name__ == "__main__":
    test_logging_paths()
    test_backend_logging()
    
    print("\n=== Summary ===")
    print("1. Check that log files are in the correct directory based on environment")
    print("2. Verify that frontend.log will be created in the same directory as api.log and error.log")
    print("3. Test the debug-logs.tsx component in the frontend to ensure it opens the correct files")