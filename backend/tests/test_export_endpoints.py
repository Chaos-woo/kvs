#!/usr/bin/env python3
"""
Test script for KV export endpoints
"""
import requests
import json

def test_export_endpoints():
    base_url = "http://localhost:5000/api"
    
    print("Testing KV Export Endpoints")
    print("=" * 50)
    
    # Test the export stats endpoint
    print("\n1. Testing Export Stats Endpoint:")
    try:
        response = requests.get(f'{base_url}/kv/export/stats', timeout=5)
        print(f'   Status Code: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Response: {json.dumps(data, indent=4)}')
        else:
            print(f'   Error: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'   Error connecting to server: {e}')
        print("   Make sure the backend server is running on localhost:5000")
        return False
    
    # Test the export data endpoint
    print("\n2. Testing Export Data Endpoint:")
    try:
        response = requests.get(f'{base_url}/kv/export', timeout=10)
        print(f'   Status Code: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Status: {data.get("status")}')
            print(f'   Count: {data.get("count")}')
            if data.get('data') and len(data['data']) > 0:
                print(f'   First record: {json.dumps(data["data"][0], indent=4)}')
                
                # Test JSONL format
                print("\n3. Testing JSONL Format:")
                jsonl_content = '\n'.join([json.dumps(record) for record in data['data']])
                print(f'   JSONL sample (first line): {jsonl_content.split(chr(10))[0]}')
                print(f'   Total lines: {len(jsonl_content.split(chr(10)))}')
            else:
                print('   No data records found')
        else:
            print(f'   Error: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f'   Error connecting to server: {e}')
        return False
    
    print("\n" + "=" * 50)
    print("Export endpoints test completed!")
    return True

if __name__ == "__main__":
    test_export_endpoints()