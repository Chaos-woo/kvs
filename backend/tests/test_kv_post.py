import requests
import json

def test_kv_post():
    """Test script to reproduce the POST /api/v1/kv error"""
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    # Test data
    test_data = {
        "key": "test_key",
        "vals": ["test_value_1", "test_value_2"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"[DEBUG_LOG] Sending POST request to {url}")
    print(f"[DEBUG_LOG] Data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"[DEBUG_LOG] Response status code: {response.status_code}")
        print(f"[DEBUG_LOG] Response headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"[DEBUG_LOG] Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"[DEBUG_LOG] Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("[DEBUG_LOG] Connection error - make sure Flask server is running on 127.0.0.1:5000")
    except Exception as e:
        print(f"[DEBUG_LOG] Error: {str(e)}")

if __name__ == "__main__":
    test_kv_post()