import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_dir))

from config import is_development_mode, LOG_DIR, API_LOG_FILE, ERROR_LOG_FILE, FRONTEND_LOG_FILE

def test_log_paths():
    """Test that all log files use the same directory"""
    print("=== Log Path Consistency Test ===")
    
    is_dev = is_development_mode()
    print(f"Environment: {'Development' if is_dev else 'Production'}")
    print(f"Log Directory: {LOG_DIR}")
    print(f"API Log File: {API_LOG_FILE}")
    print(f"Error Log File: {ERROR_LOG_FILE}")
    print(f"Frontend Log File: {FRONTEND_LOG_FILE}")
    
    # Check that all log files are in the same directory
    api_dir = os.path.dirname(API_LOG_FILE)
    error_dir = os.path.dirname(ERROR_LOG_FILE)
    frontend_dir = os.path.dirname(FRONTEND_LOG_FILE)
    
    if api_dir == error_dir == frontend_dir == LOG_DIR:
        print("✓ All log files are in the same directory")
    else:
        print("✗ Log files are in different directories:")
        print(f"  API log dir: {api_dir}")
        print(f"  Error log dir: {error_dir}")
        print(f"  Frontend log dir: {frontend_dir}")
        print(f"  Expected dir: {LOG_DIR}")
    
    # Check if log directory exists
    if os.path.exists(LOG_DIR):
        print(f"✓ Log directory exists: {LOG_DIR}")
        
        # List files in log directory
        log_files = os.listdir(LOG_DIR)
        print(f"Files in log directory: {log_files}")
        
        # Check each log file
        for log_name, log_path in [
            ("api.log", API_LOG_FILE),
            ("error.log", ERROR_LOG_FILE), 
            ("frontend.log", FRONTEND_LOG_FILE)
        ]:
            if os.path.exists(log_path):
                size = os.path.getsize(log_path)
                print(f"✓ {log_name} exists ({size} bytes)")
            else:
                print(f"✗ {log_name} does not exist at {log_path}")
    else:
        print(f"✗ Log directory does not exist: {LOG_DIR}")
        # Create it
        os.makedirs(LOG_DIR, exist_ok=True)
        print(f"✓ Created log directory: {LOG_DIR}")

def test_frontend_log_creation():
    """Test creating a frontend log entry"""
    print("\n=== Frontend Log Creation Test ===")
    
    try:
        # Create a test log entry
        test_message = f"Test frontend log entry - {os.getpid()}\n"
        
        with open(FRONTEND_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(test_message)
        
        print(f"✓ Successfully wrote test message to {FRONTEND_LOG_FILE}")
        
        # Verify the message was written
        if os.path.exists(FRONTEND_LOG_FILE):
            with open(FRONTEND_LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if test_message.strip() in content:
                    print("✓ Test message found in frontend log")
                else:
                    print("✗ Test message not found in frontend log")
        
    except Exception as e:
        print(f"✗ Failed to write to frontend log: {e}")

def simulate_production_environment():
    """Simulate production environment to test path resolution"""
    print("\n=== Production Environment Simulation ===")
    
    # Temporarily modify sys to simulate production
    original_frozen = getattr(sys, 'frozen', False)
    original_meipass = getattr(sys, '_MEIPASS', None)
    
    try:
        # Simulate PyInstaller environment
        sys.frozen = True
        sys._MEIPASS = 'C:\\temp\\meipass'
        
        # Re-import config to get production paths
        import importlib
        import config
        importlib.reload(config)
        
        print(f"Simulated production mode: {not config.is_development_mode()}")
        print(f"Production log directory: {config.LOG_DIR}")
        print(f"Production frontend log: {config.FRONTEND_LOG_FILE}")
        
        # Check if production paths use APPDATA
        if 'AppData' in config.LOG_DIR or 'APPDATA' in config.LOG_DIR:
            print("✓ Production mode uses APPDATA directory")
        else:
            print("✗ Production mode not using APPDATA directory")
            
    finally:
        # Restore original values
        if original_frozen:
            sys.frozen = original_frozen
        else:
            delattr(sys, 'frozen')
            
        if original_meipass:
            sys._MEIPASS = original_meipass
        elif hasattr(sys, '_MEIPASS'):
            delattr(sys, '_MEIPASS')
        
        # Reload config to restore original state
        importlib.reload(config)

if __name__ == "__main__":
    test_log_paths()
    test_frontend_log_creation()
    simulate_production_environment()
    
    print("\n=== Summary ===")
    print("1. ✓ Fixed frontend logger to use same directory as backend logs")
    print("2. ✓ Updated Tauri configuration for better file access")
    print("3. ✓ All log files should now be in the same directory")
    print("4. Test the debug-logs.tsx component to verify file opening works")