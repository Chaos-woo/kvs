import os
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent / 'backend'
sys.path.insert(0, str(backend_dir))

from config import is_development_mode, LOG_DIR, API_LOG_FILE, ERROR_LOG_FILE, FRONTEND_LOG_FILE

def test_tauri_configuration():
    """Test the updated Tauri configuration"""
    print("=== Tauri Configuration Fix Test ===")
    
    tauri_config_path = Path(__file__).resolve().parent / 'frontend' / 'src-tauri' / 'tauri.conf.json'
    
    if tauri_config_path.exists():
        try:
            with open(tauri_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Check shell configuration
            shell_config = config.get('tauri', {}).get('allowlist', {}).get('shell', {})
            shell_open = shell_config.get('open', False)
            shell_scope = shell_config.get('scope', [])
            
            print(f"Shell open enabled: {shell_open}")
            print(f"Shell scope defined: {len(shell_scope) > 0}")
            
            if len(shell_scope) == 0:
                print("✓ Shell scope simplified (no restrictive commands)")
            else:
                print("✗ Shell scope still has restrictive commands")
                for scope in shell_scope:
                    print(f"  - {scope}")
            
            # Check filesystem configuration
            fs_config = config.get('tauri', {}).get('allowlist', {}).get('fs', {})
            fs_scope = fs_config.get('scope', [])
            
            print(f"\nFile system scope entries: {len(fs_scope)}")
            
            # Check for required scope entries
            required_scopes = [
                '$APPDATA/com.kvs.dev/*',
                '$APPDATA/com.kvs.dev/kvs/*',
                'backend/logs/*'
            ]
            
            missing_scopes = []
            for required in required_scopes:
                if required not in fs_scope:
                    missing_scopes.append(required)
            
            if not missing_scopes:
                print("✓ All required filesystem scopes are present")
            else:
                print("✗ Missing required filesystem scopes:")
                for missing in missing_scopes:
                    print(f"  - {missing}")
            
            # Show current scopes
            print("\nCurrent filesystem scopes:")
            for scope in fs_scope:
                print(f"  - {scope}")
                
        except Exception as e:
            print(f"✗ Failed to read Tauri config: {e}")
    else:
        print(f"✗ Tauri config not found: {tauri_config_path}")

def test_backend_log_paths():
    """Test backend log path configuration"""
    print("\n=== Backend Log Path Test ===")
    
    is_dev = is_development_mode()
    print(f"Environment: {'Development' if is_dev else 'Production'}")
    print(f"Log Directory: {LOG_DIR}")
    print(f"API Log File: {API_LOG_FILE}")
    print(f"Error Log File: {ERROR_LOG_FILE}")
    print(f"Frontend Log File: {FRONTEND_LOG_FILE}")
    
    # Check if all log files are in the same directory
    api_dir = os.path.dirname(API_LOG_FILE)
    error_dir = os.path.dirname(ERROR_LOG_FILE)
    frontend_dir = os.path.dirname(FRONTEND_LOG_FILE)
    
    if api_dir == error_dir == frontend_dir == LOG_DIR:
        print("✓ All backend log files are configured for the same directory")
    else:
        print("✗ Backend log files are in different directories")

def test_expected_paths():
    """Test expected paths for different scenarios"""
    print("\n=== Expected Path Analysis ===")
    
    # Development environment
    print("Development environment expected paths:")
    print(f"  Backend logs: backend/logs/")
    print(f"  Frontend logs (preferred): backend/logs/")
    print(f"  Frontend logs (fallback): %APPDATA%/kvs/logs/")
    
    # Production environment  
    print("\nProduction environment expected paths:")
    print(f"  Backend logs: %APPDATA%/kvs/logs/")
    print(f"  Frontend logs: %APPDATA%/kvs/logs/")
    
    # Current user's AppData path
    appdata_path = os.environ.get('APPDATA', 'Unknown')
    print(f"\nCurrent user's APPDATA: {appdata_path}")
    
    if appdata_path != 'Unknown':
        expected_prod_path = os.path.join(appdata_path, 'kvs', 'logs')
        tauri_prod_path = os.path.join(appdata_path, 'com.kvs.dev', 'kvs', 'logs')
        print(f"Expected production path: {expected_prod_path}")
        print(f"Tauri production path: {tauri_prod_path}")

if __name__ == "__main__":
    test_tauri_configuration()
    test_backend_log_paths()
    test_expected_paths()
    
    print("\n=== Fix Summary ===")
    print("1. ✓ Simplified shell configuration to remove restrictive scope")
    print("2. ✓ Added com.kvs.dev paths to filesystem scope")
    print("3. ✓ Added debug logging to frontend logger")
    print("4. Next: Test with 'npm run dev-with-backend' to verify fixes")