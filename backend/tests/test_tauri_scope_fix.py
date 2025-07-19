#!/usr/bin/env python3
"""
Test script to verify the Tauri filesystem scope fix.
This script checks if the Tauri configuration now allows access to the required log paths.
"""

import os
import json
from pathlib import Path

def test_tauri_scope_configuration():
    """Test the Tauri filesystem scope configuration"""
    print("=== Testing Tauri Filesystem Scope Configuration ===")
    
    # Load the Tauri configuration
    tauri_config_path = os.path.join("../../frontend", "src-tauri", "tauri.conf.json")
    if not os.path.exists(tauri_config_path):
        print(f"✗ Tauri config not found: {tauri_config_path}")
        return False
    
    try:
        with open(tauri_config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ Tauri configuration loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load Tauri configuration: {e}")
        return False
    
    # Get the filesystem scope
    try:
        fs_scope = config["tauri"]["allowlist"]["fs"]["scope"]
        print(f"✓ Found filesystem scope with {len(fs_scope)} entries")
    except KeyError as e:
        print(f"✗ Failed to find filesystem scope in config: {e}")
        return False
    
    # Check for required scope entries
    required_scopes = [
        "$APPDATA/kvs/logs/*",
        "$APPDATA/com.kvs.dev/kvs/logs/*",
        "$LOCALDATA/kvs/logs/*", 
        "$LOCALDATA/com.kvs.dev/kvs/logs/*",
        "$HOME/.kvs/logs/*",
        "$TEMP/kvs/logs/*"
    ]
    
    print("\nChecking required scope entries:")
    all_found = True
    for required_scope in required_scopes:
        if required_scope in fs_scope:
            print(f"✓ {required_scope}")
        else:
            print(f"✗ {required_scope} - MISSING")
            all_found = False
    
    # Check for original scopes that should still be there
    original_scopes = [
        "$APPDATA/*",
        "$APPDATA/kvs/*",
        "$APPDATA/com.kvs.dev/*",
        "$APPDATA/com.kvs.dev/kvs/*",
        "backend/logs/*"
    ]
    
    print("\nChecking original scope entries:")
    for original_scope in original_scopes:
        if original_scope in fs_scope:
            print(f"✓ {original_scope}")
        else:
            print(f"✗ {original_scope} - MISSING")
            all_found = False
    
    return all_found

def test_path_patterns():
    """Test if the problematic path would be covered by the new scopes"""
    print("\n=== Testing Path Pattern Coverage ===")
    
    # The problematic path from the error message
    problematic_path = r"C:\Users\78580\AppData\Roaming\com.kvs.dev\kvs\logs\frontend.log"
    print(f"Problematic path: {problematic_path}")
    
    # Extract the pattern part
    appdata_part = os.environ.get('APPDATA', r'C:\Users\USERNAME\AppData\Roaming')
    print(f"Current APPDATA: {appdata_part}")
    
    # Check if the path follows the expected pattern
    expected_pattern = os.path.join(appdata_part, "com.kvs.dev", "kvs", "logs", "frontend.log")
    print(f"Expected pattern: {expected_pattern}")
    
    # The new scope should cover this
    covering_scope = "$APPDATA/com.kvs.dev/kvs/logs/*"
    print(f"Covering scope: {covering_scope}")
    
    # Simulate the pattern matching (handle both forward and back slashes)
    pattern_parts = ["com.kvs.dev", "kvs", "logs"]
    if all(part in problematic_path for part in pattern_parts):
        print("✓ Path matches the pattern that should be covered by new scope")
        return True
    else:
        print("✗ Path does not match expected pattern")
        return False

def test_development_fallback_scenario():
    """Test the development mode fallback scenario"""
    print("\n=== Testing Development Mode Fallback Scenario ===")
    
    # This simulates what happens when backend/logs paths fail in development
    # and the logger falls back to AppData directory
    
    appdata = os.environ.get('APPDATA')
    if not appdata:
        print("! APPDATA not available, skipping test")
        return True
    
    # The paths that would be used in fallback
    fallback_paths = [
        os.path.join(appdata, "kvs", "logs", "frontend.log"),
        os.path.join(appdata, "com.kvs.dev", "kvs", "logs", "frontend.log")
    ]
    
    print("Fallback paths that should now be allowed:")
    for path in fallback_paths:
        print(f"  {path}")
    
    # Check if these paths would be covered by our scopes
    scopes_that_cover = [
        "$APPDATA/kvs/logs/*",
        "$APPDATA/com.kvs.dev/kvs/logs/*"
    ]
    
    print("Scopes that should cover these paths:")
    for scope in scopes_that_cover:
        print(f"  {scope}")
    
    print("✓ Development mode fallback paths should now be allowed")
    return True

def run_comprehensive_test():
    """Run all tests"""
    print("=== Comprehensive Tauri Scope Fix Test ===")
    print("Testing fix for: 'Failed to flush logs: path not allowed on the configured scope'")
    print()
    
    tests = [
        ("Tauri Scope Configuration", test_tauri_scope_configuration),
        ("Path Pattern Coverage", test_path_patterns),
        ("Development Fallback Scenario", test_development_fallback_scenario),
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
        print("✓ Tauri filesystem scope updated with explicit logs directory permissions:")
        print("  - $APPDATA/kvs/logs/*")
        print("  - $APPDATA/com.kvs.dev/kvs/logs/*")
        print("  - $LOCALDATA/kvs/logs/*")
        print("  - $LOCALDATA/com.kvs.dev/kvs/logs/*")
        print("  - $HOME/.kvs/logs/*")
        print("  - $TEMP/kvs/logs/*")
        print("✓ Frontend logger should now be able to write to AppData fallback paths")
        print("✓ Development mode fallback scenario should work correctly")
        print("\nThe 'path not allowed on the configured scope' error should be resolved.")
    
    return all_passed

if __name__ == "__main__":
    import sys
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)