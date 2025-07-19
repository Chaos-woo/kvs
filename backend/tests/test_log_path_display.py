#!/usr/bin/env python3
"""
Test script to verify the log path display functionality.
This script will test both development and production scenarios.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path

def test_log_paths():
    """Test the log path display functionality"""
    print("=== Testing Log Path Display Functionality ===")
    
    # Check if we're in the correct directory
    if not os.path.exists("..") or not os.path.exists("../../frontend"):
        print("Error: Please run this script from the project root directory")
        return False
    
    # Test 1: Check backend log configuration
    print("\n1. Testing Backend Log Configuration...")
    
    # Import backend config to check paths
    sys.path.append('..')
    try:
        import config
        print(f"   Development mode: {config.is_development_mode()}")
        print(f"   LOG_DIR: {config.LOG_DIR}")
        print(f"   API_LOG_FILE: {config.API_LOG_FILE}")
        print(f"   ERROR_LOG_FILE: {config.ERROR_LOG_FILE}")
        print(f"   FRONTEND_LOG_FILE: {config.FRONTEND_LOG_FILE}")
        
        # Check if log directory exists
        if os.path.exists(config.LOG_DIR):
            print(f"   ✓ Log directory exists: {config.LOG_DIR}")
        else:
            print(f"   ✗ Log directory does not exist: {config.LOG_DIR}")
            
        # Check expected paths
        if config.is_development_mode():
            expected_path = os.path.join(os.getcwd(), "backend", "logs")
            if os.path.normpath(config.LOG_DIR) == os.path.normpath(expected_path):
                print("   ✓ Development log path is correct")
            else:
                print(f"   ✗ Development log path incorrect. Expected: {expected_path}, Got: {config.LOG_DIR}")
        else:
            appdata = os.environ.get('APPDATA')
            if appdata:
                expected_path = os.path.join(appdata, "kvs", "logs")
                if os.path.normpath(config.LOG_DIR) == os.path.normpath(expected_path):
                    print("   ✓ Production log path is correct")
                else:
                    print(f"   ✗ Production log path incorrect. Expected: {expected_path}, Got: {config.LOG_DIR}")
            else:
                print("   ! APPDATA environment variable not found")
                
    except Exception as e:
        print(f"   ✗ Error importing backend config: {e}")
        return False
    
    # Test 2: Check if log files exist and are being written to
    print("\n2. Testing Log File Creation...")
    
    log_files = [config.API_LOG_FILE, config.ERROR_LOG_FILE, config.FRONTEND_LOG_FILE]
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"   ✓ Log file exists: {log_file}")
            # Check if file has recent content
            stat = os.stat(log_file)
            if stat.st_size > 0:
                print(f"     File size: {stat.st_size} bytes")
            else:
                print("     File is empty")
        else:
            print(f"   ✗ Log file does not exist: {log_file}")
    
    # Test 3: Check frontend logger configuration
    print("\n3. Testing Frontend Logger Configuration...")
    
    # Check if the frontend logger TypeScript file exists
    frontend_logger_path = os.path.join("../../frontend", "src", "utils", "logger.ts")
    if os.path.exists(frontend_logger_path):
        print(f"   ✓ Frontend logger file exists: {frontend_logger_path}")
        
        # Read the file to check the path logic
        with open(frontend_logger_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for development mode detection
        if "isDevelopmentMode" in content:
            print("   ✓ Frontend has development mode detection")
        else:
            print("   ✗ Frontend missing development mode detection")
            
        # Check for backend/logs path handling
        if "backend/logs" in content or "backend', 'logs'" in content:
            print("   ✓ Frontend has backend/logs path handling")
        else:
            print("   ✗ Frontend missing backend/logs path handling")
            
        # Check for APPDATA path handling
        if "appDataDir" in content and "kvs" in content:
            print("   ✓ Frontend has APPDATA/kvs path handling")
        else:
            print("   ✗ Frontend missing APPDATA/kvs path handling")
            
    else:
        print(f"   ✗ Frontend logger file not found: {frontend_logger_path}")
    
    # Test 4: Check debug-logs component
    print("\n4. Testing Debug Logs Component...")
    
    debug_logs_path = os.path.join("../../frontend", "src", "components", "debug-logs.tsx")
    if os.path.exists(debug_logs_path):
        print(f"   ✓ Debug logs component exists: {debug_logs_path}")
        
        with open(debug_logs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check which method is being called
        if "getLogFilePath" in content:
            print("   ! Debug component calls getLogFilePath() - this might be the issue!")
            print("     getLogFilePath() returns directory path, not file path")
        if "getLogDirectoryPath" in content:
            print("   ✓ Debug component calls getLogDirectoryPath()")
            
        # Check for the "显示日志路径" button
        if "显示日志路径" in content:
            print("   ✓ Found '显示日志路径' button")
        else:
            print("   ✗ '显示日志路径' button not found")
            
    else:
        print(f"   ✗ Debug logs component not found: {debug_logs_path}")
    
    print("\n=== Test Summary ===")
    print("The issue appears to be in the debug-logs component:")
    print("- It calls logger.getLogFilePath() which returns the directory path")
    print("- The method name is misleading - it should be getLogDirectoryPath()")
    print("- Or the component should call the correct method for displaying the directory path")
    
    return True

if __name__ == "__main__":
    test_log_paths()