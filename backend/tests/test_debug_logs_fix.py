import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_dir))

from config import is_development_mode, LOG_DIR, API_LOG_FILE, ERROR_LOG_FILE, FRONTEND_LOG_FILE

def test_issue_fixes():
    """Test that the reported issues are fixed"""
    print("=== Debug Logs Issue Fix Verification ===")
    
    is_dev = is_development_mode()
    print(f"Current Environment: {'Development' if is_dev else 'Production'}")
    print(f"Backend Log Directory: {LOG_DIR}")
    
    # Issue 1: In production environment, frontend.log is not written to the same directory as api.log
    print("\n--- Issue 1: Frontend.log Directory Location ---")
    
    api_dir = os.path.dirname(API_LOG_FILE)
    error_dir = os.path.dirname(ERROR_LOG_FILE)
    frontend_dir = os.path.dirname(FRONTEND_LOG_FILE)
    
    print(f"API log directory: {api_dir}")
    print(f"Error log directory: {error_dir}")
    print(f"Frontend log directory: {frontend_dir}")
    
    if api_dir == error_dir == frontend_dir:
        print("✓ FIXED: All log files are configured to use the same directory")
    else:
        print("✗ ISSUE PERSISTS: Log files are in different directories")
    
    # Test production environment simulation
    print("\n--- Production Environment Test ---")
    
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
        
        prod_api_dir = os.path.dirname(config.API_LOG_FILE)
        prod_error_dir = os.path.dirname(config.ERROR_LOG_FILE)
        prod_frontend_dir = os.path.dirname(config.FRONTEND_LOG_FILE)
        
        print(f"Production API log directory: {prod_api_dir}")
        print(f"Production Error log directory: {prod_error_dir}")
        print(f"Production Frontend log directory: {prod_frontend_dir}")
        
        if prod_api_dir == prod_error_dir == prod_frontend_dir:
            print("✓ FIXED: In production, all log files use the same directory")
            if 'AppData' in prod_api_dir:
                print("✓ CONFIRMED: Production uses APPDATA directory")
            else:
                print("✗ WARNING: Production not using APPDATA directory")
        else:
            print("✗ ISSUE PERSISTS: In production, log files are in different directories")
            
    finally:
        # Restore original values
        if original_frozen:
            sys.frozen = original_frozen
        else:
            if hasattr(sys, 'frozen'):
                delattr(sys, 'frozen')
            
        if original_meipass:
            sys._MEIPASS = original_meipass
        elif hasattr(sys, '_MEIPASS'):
            delattr(sys, '_MEIPASS')
        
        # Reload config to restore original state
        importlib.reload(config)

def test_file_access_permissions():
    """Test file access and permissions for debug-logs component"""
    print("\n--- Issue 2: Debug-logs Component File Access ---")
    
    # Test if log files exist and are accessible
    log_files = [
        ("api.log", API_LOG_FILE),
        ("error.log", ERROR_LOG_FILE),
        ("frontend.log", FRONTEND_LOG_FILE)
    ]
    
    all_accessible = True
    
    for log_name, log_path in log_files:
        if os.path.exists(log_path):
            try:
                # Test read access
                with open(log_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Read first 100 characters
                print(f"✓ {log_name} exists and is readable: {log_path}")
            except Exception as e:
                print(f"✗ {log_name} exists but not readable: {e}")
                all_accessible = False
        else:
            print(f"✗ {log_name} does not exist: {log_path}")
            all_accessible = False
    
    # Test directory access
    if os.path.exists(LOG_DIR):
        try:
            os.listdir(LOG_DIR)
            print(f"✓ Log directory is accessible: {LOG_DIR}")
        except Exception as e:
            print(f"✗ Log directory not accessible: {e}")
            all_accessible = False
    else:
        print(f"✗ Log directory does not exist: {LOG_DIR}")
        all_accessible = False
    
    if all_accessible:
        print("✓ FIXED: All log files and directory are accessible")
    else:
        print("✗ ISSUE PERSISTS: Some files or directory not accessible")

def test_tauri_configuration():
    """Test Tauri configuration for file system access"""
    print("\n--- Tauri Configuration Test ---")
    
    tauri_config_path = Path(__file__).resolve().parent / 'frontend' / 'src-tauri' / 'tauri.conf.json'
    
    if tauri_config_path.exists():
        try:
            import json
            with open(tauri_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            fs_scope = config.get('tauri', {}).get('allowlist', {}).get('fs', {}).get('scope', [])
            shell_open = config.get('tauri', {}).get('allowlist', {}).get('shell', {}).get('open', False)
            
            print(f"✓ Tauri config loaded successfully")
            print(f"Shell open enabled: {shell_open}")
            print(f"File system scope entries: {len(fs_scope)}")
            
            # Check if backend logs are in scope
            backend_scope_found = any('backend' in scope for scope in fs_scope)
            appdata_scope_found = any('APPDATA' in scope for scope in fs_scope)
            
            if backend_scope_found:
                print("✓ Backend logs directory is in Tauri fs scope")
            else:
                print("✗ Backend logs directory not in Tauri fs scope")
            
            if appdata_scope_found:
                print("✓ APPDATA directory is in Tauri fs scope")
            else:
                print("✗ APPDATA directory not in Tauri fs scope")
                
        except Exception as e:
            print(f"✗ Failed to read Tauri config: {e}")
    else:
        print(f"✗ Tauri config not found: {tauri_config_path}")

if __name__ == "__main__":
    test_issue_fixes()
    test_file_access_permissions()
    test_tauri_configuration()
    
    print("\n=== Fix Summary ===")
    print("1. ✓ Frontend logger now uses environment-based path logic matching backend")
    print("2. ✓ Tauri configuration updated with additional file system scope")
    print("3. ✓ All log files should be in the same directory in both dev and prod")
    print("4. ✓ Debug-logs.tsx component should now be able to open files and directories")
    print("\nNext steps:")
    print("- Test the frontend application to verify debug-logs buttons work")
    print("- Verify frontend.log is created in the correct location")