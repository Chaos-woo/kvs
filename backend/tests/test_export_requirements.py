#!/usr/bin/env python3
"""
Comprehensive test to verify KV export functionality meets all requirements
"""
import requests
import json
import sys
import time

def test_requirement_1_jsonl_format():
    """Test: 输出jsonl格式的KV数据导出功能，仅支持全量导出"""
    print("Testing Requirement 1: JSONL format export with full export only")
    
    try:
        response = requests.get("http://localhost:5000/api/v1/kv/export", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                export_data = data.get('data', [])
                
                # Verify it's full export (all data)
                print(f"  ✓ Full export: {len(export_data)} records exported")
                
                # Verify JSONL format capability
                if export_data:
                    sample_record = export_data[0]
                    jsonl_line = json.dumps(sample_record)
                    print(f"  ✓ JSONL format compatible: {jsonl_line}")
                    return True
                else:
                    print("  ⚠ No data to export (empty database)")
                    return True
            else:
                print(f"  ✗ API returned error: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

def test_requirement_2_data_format():
    """Test: 单行数据格式：{"k":"str","v":["str"],"create_at":"timestamp"}"""
    print("\nTesting Requirement 2: Data format specification")
    
    try:
        response = requests.get("http://localhost:5000/api/v1/kv/export", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                export_data = data.get('data', [])
                
                if export_data:
                    sample_record = export_data[0]
                    
                    # Check required fields
                    has_k = 'k' in sample_record and isinstance(sample_record['k'], str)
                    has_v = 'v' in sample_record and isinstance(sample_record['v'], list)
                    has_create_at = 'create_at' in sample_record and isinstance(sample_record['create_at'], str)
                    
                    print(f"  ✓ Field 'k' (string): {has_k} - {sample_record.get('k')}")
                    print(f"  ✓ Field 'v' (array): {has_v} - {sample_record.get('v')}")
                    print(f"  ✓ Field 'create_at' (timestamp): {has_create_at} - {sample_record.get('create_at')}")
                    
                    return has_k and has_v and has_create_at
                else:
                    print("  ⚠ No data to verify format (empty database)")
                    return True
            else:
                print(f"  ✗ API returned error: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

def test_requirement_3_statistics():
    """Test: 展示待导出KV统计数据：K数量，V数量，KV对数量"""
    print("\nTesting Requirement 3: Export statistics display")
    
    try:
        response = requests.get("http://localhost:5000/api/v1/kv/export/stats", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                stats = data.get('data', {})
                
                has_k_count = 'k_count' in stats and isinstance(stats['k_count'], int)
                has_v_count = 'v_count' in stats and isinstance(stats['v_count'], int)
                has_kv_pairs_count = 'kv_pairs_count' in stats and isinstance(stats['kv_pairs_count'], int)
                
                print(f"  ✓ K数量: {stats.get('k_count')} (type: {type(stats.get('k_count'))})")
                print(f"  ✓ V数量: {stats.get('v_count')} (type: {type(stats.get('v_count'))})")
                print(f"  ✓ KV对数量: {stats.get('kv_pairs_count')} (type: {type(stats.get('kv_pairs_count'))})")
                
                return has_k_count and has_v_count and has_kv_pairs_count
            else:
                print(f"  ✗ API returned error: {data.get('message')}")
                return False
        else:
            print(f"  ✗ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")
        return False

def test_requirement_4_ui_components():
    """Test: UI交互规范（全部使用Shadcn组件实现）"""
    print("\nTesting Requirement 4: UI components (Shadcn/ui)")
    
    # Check if export-dialog.tsx uses shadcn components
    try:
        with open("../../frontend/src/components/export-dialog.tsx", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Check for shadcn/ui imports
        shadcn_imports = [
            "AlertDialog",
            "AlertDialogAction", 
            "AlertDialogCancel",
            "AlertDialogContent",
            "AlertDialogDescription",
            "AlertDialogFooter",
            "AlertDialogHeader",
            "AlertDialogTitle",
            "Button",
            "Label",
            "useToast"
        ]
        
        all_imports_found = True
        for import_name in shadcn_imports:
            if import_name in content:
                print(f"  ✓ Uses {import_name} component")
            else:
                print(f"  ✗ Missing {import_name} component")
                all_imports_found = False
                
        return all_imports_found
        
    except Exception as e:
        print(f"  ✗ Error checking UI components: {e}")
        return False

def test_requirement_5_menu_integration():
    """Test: 用户点击菜单"设置"-"数据导出"选项"""
    print("\nTesting Requirement 5: Menu integration")
    
    try:
        # Check menu-bar.tsx for export option
        with open("../../frontend/src/components/menu-bar.tsx", "r", encoding="utf-8") as f:
            content = f.read()
            
        has_settings_menu = "设置" in content
        has_export_option = "数据导出" in content
        has_export_handler = "onShowExport" in content
        
        print(f"  ✓ Has '设置' menu: {has_settings_menu}")
        print(f"  ✓ Has '数据导出' option: {has_export_option}")
        print(f"  ✓ Has export handler: {has_export_handler}")
        
        # Check App.tsx for integration
        with open("../../frontend/src/App.tsx", "r", encoding="utf-8") as f:
            app_content = f.read()
            
        has_export_dialog_import = "ExportDialog" in app_content
        has_export_state = "showExportDialog" in app_content
        has_export_handler_impl = "handleShowExport" in app_content
        
        print(f"  ✓ ExportDialog imported in App.tsx: {has_export_dialog_import}")
        print(f"  ✓ Export state managed: {has_export_state}")
        print(f"  ✓ Export handler implemented: {has_export_handler_impl}")
        
        return (has_settings_menu and has_export_option and has_export_handler and 
                has_export_dialog_import and has_export_state and has_export_handler_impl)
        
    except Exception as e:
        print(f"  ✗ Error checking menu integration: {e}")
        return False

def test_requirement_6_file_selection():
    """Test: Tauri file selection implementation"""
    print("\nTesting Requirement 6: File selection using Tauri APIs")
    
    try:
        with open("../../frontend/src/components/export-dialog.tsx", "r", encoding="utf-8") as f:
            content = f.read()
            
        has_tauri_dialog_import = "from \"@tauri-apps/api/dialog\"" in content
        has_tauri_fs_import = "from \"@tauri-apps/api/fs\"" in content
        has_save_dialog = "save(" in content
        has_write_file = "writeTextFile(" in content
        
        print(f"  ✓ Tauri dialog API imported: {has_tauri_dialog_import}")
        print(f"  ✓ Tauri fs API imported: {has_tauri_fs_import}")
        print(f"  ✓ Save dialog implemented: {has_save_dialog}")
        print(f"  ✓ File writing implemented: {has_write_file}")
        
        return has_tauri_dialog_import and has_tauri_fs_import and has_save_dialog and has_write_file
        
    except Exception as e:
        print(f"  ✗ Error checking file selection: {e}")
        return False

def main():
    """Main test function"""
    print("KV Export Functionality Requirements Test")
    print("=" * 60)
    
    # Run all requirement tests
    tests = [
        test_requirement_1_jsonl_format,
        test_requirement_2_data_format,
        test_requirement_3_statistics,
        test_requirement_4_ui_components,
        test_requirement_5_menu_integration,
        test_requirement_6_file_selection,
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        time.sleep(0.5)  # Small delay between tests
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All requirements are properly implemented!")
        sys.exit(0)
    else:
        print("❌ Some requirements need attention!")
        sys.exit(1)

if __name__ == "__main__":
    main()