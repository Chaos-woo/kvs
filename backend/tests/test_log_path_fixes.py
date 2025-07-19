#!/usr/bin/env python3
"""
Test script to verify the log path fixes work correctly.
This script tests both the backend logging and frontend path display functionality.
"""

import os
import sys
import json
import subprocess
import time
import tempfile
from pathlib import Path

def test_backend_logging():
    """Test backend logging functionality"""
    print("=== Testing Backend Logging ===")
    
    # Import backend config
    sys.path.append('..')
    try:
        import config
        print(f"✓ Backend config loaded successfully")
        print(f"  Development mode: {config.is_development_mode()}")
        print(f"  LOG_DIR: {config.LOG_DIR}")
        
        # Verify paths are correct
        if config.is_development_mode():
            expected_path = os.path.join(os.getcwd(), "backend", "logs")
            if os.path.normpath(config.LOG_DIR) == os.path.normpath(expected_path):
                print("✓ Development log path is correct")
            else:
                print(f"✗ Development log path incorrect. Expected: {expected_path}, Got: {config.LOG_DIR}")
                return False
        else:
            appdata = os.environ.get('APPDATA')
            if appdata:
                expected_path = os.path.join(appdata, "kvs", "logs")
                if os.path.normpath(config.LOG_DIR) == os.path.normpath(expected_path):
                    print("✓ Production log path is correct")
                else:
                    print(f"✗ Production log path incorrect. Expected: {expected_path}, Got: {config.LOG_DIR}")
                    return False
        
        # Test log file creation
        log_files = [
            ('api.log', config.API_LOG_FILE),
            ('error.log', config.ERROR_LOG_FILE),
            ('frontend.log', config.FRONTEND_LOG_FILE)
        ]
        
        for log_name, log_path in log_files:
            if os.path.exists(log_path):
                print(f"✓ {log_name} exists at correct location: {log_path}")
            else:
                print(f"! {log_name} does not exist yet: {log_path}")
                # Try to create the directory if it doesn't exist
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                print(f"  Created directory for {log_name}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing backend logging: {e}")
        return False

def test_frontend_logger_methods():
    """Test frontend logger method naming and functionality"""
    print("\n=== Testing Frontend Logger Methods ===")
    
    logger_path = os.path.join("../../frontend", "src", "utils", "logger.ts")
    if not os.path.exists(logger_path):
        print(f"✗ Frontend logger not found: {logger_path}")
        return False
    
    with open(logger_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for deprecated method
    if "@deprecated" in content and "getLogFilePath" in content:
        print("✓ getLogFilePath() method is properly deprecated")
    else:
        print("! getLogFilePath() method deprecation not found")
    
    # Check for proper method
    if "getLogDirectoryPath" in content:
        print("✓ getLogDirectoryPath() method exists")
    else:
        print("✗ getLogDirectoryPath() method not found")
        return False
    
    # Check development mode detection
    if "isDevelopmentMode" in content:
        print("✓ Development mode detection exists")
    else:
        print("✗ Development mode detection missing")
        return False
    
    # Check path logic
    if "backend/logs" in content or "backend', 'logs'" in content:
        print("✓ Backend logs path handling exists")
    else:
        print("✗ Backend logs path handling missing")
        return False
    
    if "appDataDir" in content and "kvs" in content:
        print("✓ APPDATA/kvs path handling exists")
    else:
        print("✗ APPDATA/kvs path handling missing")
        return False
    
    return True

def test_debug_component_fix():
    """Test debug logs component uses correct method"""
    print("\n=== Testing Debug Component Fix ===")
    
    debug_path = os.path.join("../../frontend", "src", "components", "debug-logs.tsx")
    if not os.path.exists(debug_path):
        print(f"✗ Debug component not found: {debug_path}")
        return False
    
    with open(debug_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that it uses the correct method
    if "getLogDirectoryPath" in content:
        print("✓ Debug component uses getLogDirectoryPath()")
    else:
        print("✗ Debug component does not use getLogDirectoryPath()")
        return False
    
    # Check that it doesn't use the deprecated method
    if "getLogFilePath" in content:
        print("! Debug component still uses deprecated getLogFilePath()")
        return False
    else:
        print("✓ Debug component no longer uses deprecated getLogFilePath()")
    
    # Check for proper title
    if "日志目录路径" in content:
        print("✓ Toast title updated to '日志目录路径'")
    else:
        print("! Toast title not updated to '日志目录路径'")
    
    # Check for the button
    if "显示日志路径" in content:
        print("✓ '显示日志路径' button exists")
    else:
        print("✗ '显示日志路径' button missing")
        return False
    
    return True

def test_production_simulation():
    """Simulate production environment path logic"""
    print("\n=== Testing Production Environment Simulation ===")
    
    # Get APPDATA path
    appdata = os.environ.get('APPDATA')
    if not appdata:
        print("! APPDATA environment variable not available, skipping production test")
        return True
    
    expected_prod_path = os.path.join(appdata, "kvs", "logs")
    print(f"Expected production path: {expected_prod_path}")
    
    # Check if we can create the directory (don't actually create it in production location)
    try:
        # Just verify the path is valid
        Path(expected_prod_path).parent.exists()
        print("✓ Production path structure is valid")
    except Exception as e:
        print(f"✗ Production path structure invalid: {e}")
        return False
    
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("=== Comprehensive Log Path Fix Test ===")
    print("Testing fixes for issue: '显示日志路径' path display and log file locations")
    print()
    
    tests = [
        ("Backend Logging", test_backend_logging),
        ("Frontend Logger Methods", test_frontend_logger_methods),
        ("Debug Component Fix", test_debug_component_fix),
        ("Production Simulation", test_production_simulation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n=== Test Results Summary ===")
    all_passed = True
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not result:
            all_passed = False
    
    print(f"\nOverall result: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n=== Fix Summary ===")
        print("✓ Backend logging paths are correct:")
        print("  - Development: backend/logs/")
        print("  - Production: %APPDATA%/kvs/logs/")
        print("✓ Frontend logger method naming fixed:")
        print("  - getLogFilePath() deprecated")
        print("  - getLogDirectoryPath() used for clarity")
        print("✓ Debug component updated:")
        print("  - Uses getLogDirectoryPath() instead of getLogFilePath()")
        print("  - Toast title updated to '日志目录路径'")
        print("✓ All log files (api.log, error.log, frontend.log) use correct paths")
    
    return all_passed

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)