import requests
import json

def test_invalid_json():
    """Test with invalid JSON data"""
    print("[DEBUG_LOG] Testing invalid JSON...")
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    try:
        response = requests.post(
            url,
            data="invalid json data",
            headers={'Content-Type': 'application/json'}
        )
        print(f"[DEBUG_LOG] Invalid JSON - Status: {response.status_code}")
        try:
            print(f"[DEBUG_LOG] Response: {response.json()}")
        except:
            print(f"[DEBUG_LOG] Response text: {response.text}")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {e}")

def test_missing_key():
    """Test with missing key field"""
    print("[DEBUG_LOG] Testing missing key...")
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    test_data = {
        "vals": ["value1", "value2"]
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"[DEBUG_LOG] Missing key - Status: {response.status_code}")
        print(f"[DEBUG_LOG] Response: {response.json()}")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {e}")

def test_missing_vals():
    """Test with missing vals field"""
    print("[DEBUG_LOG] Testing missing vals...")
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    test_data = {
        "key": "test_key"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"[DEBUG_LOG] Missing vals - Status: {response.status_code}")
        print(f"[DEBUG_LOG] Response: {response.json()}")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {e}")

def test_empty_vals():
    """Test with empty vals array"""
    print("[DEBUG_LOG] Testing empty vals...")
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    test_data = {
        "key": "test_key",
        "vals": []
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"[DEBUG_LOG] Empty vals - Status: {response.status_code}")
        print(f"[DEBUG_LOG] Response: {response.json()}")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {e}")

def test_invalid_vals_type():
    """Test with invalid vals type"""
    print("[DEBUG_LOG] Testing invalid vals type...")
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    test_data = {
        "key": "test_key",
        "vals": "not_an_array"
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"[DEBUG_LOG] Invalid vals type - Status: {response.status_code}")
        print(f"[DEBUG_LOG] Response: {response.json()}")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {e}")

def test_very_long_data():
    """Test with very long key and values"""
    print("[DEBUG_LOG] Testing very long data...")
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    long_key = "x" * 10000
    long_vals = ["y" * 10000 for _ in range(100)]
    
    test_data = {
        "key": long_key,
        "vals": long_vals
    }
    
    try:
        response = requests.post(url, json=test_data)
        print(f"[DEBUG_LOG] Very long data - Status: {response.status_code}")
        try:
            resp_json = response.json()
            print(f"[DEBUG_LOG] Response status: {resp_json.get('status')}")
            if resp_json.get('status') == 'error':
                print(f"[DEBUG_LOG] Error message: {resp_json.get('message')}")
        except:
            print(f"[DEBUG_LOG] Response text: {response.text[:500]}...")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {e}")

def test_no_content_type():
    """Test without Content-Type header"""
    print("[DEBUG_LOG] Testing without Content-Type header...")
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    test_data = {
        "key": "test_key",
        "vals": ["value1", "value2"]
    }
    
    try:
        response = requests.post(url, data=json.dumps(test_data))
        print(f"[DEBUG_LOG] No Content-Type - Status: {response.status_code}")
        try:
            print(f"[DEBUG_LOG] Response: {response.json()}")
        except:
            print(f"[DEBUG_LOG] Response text: {response.text}")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {e}")

if __name__ == "__main__":
    print("[DEBUG_LOG] Starting edge case tests...")
    
    test_invalid_json()
    print()
    test_missing_key()
    print()
    test_missing_vals()
    print()
    test_empty_vals()
    print()
    test_invalid_vals_type()
    print()
    test_very_long_data()
    print()
    test_no_content_type()
    
    print("[DEBUG_LOG] Edge case tests completed")