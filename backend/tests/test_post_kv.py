import requests
import json

def test_post_kv():
    """Test script to reproduce the POST /api/v1/kv 500 error"""
    
    url = "http://127.0.0.1:5000/api/v1/kv"
    
    # Test data
    test_data = {
        "key": "test_key",
        "vals": ["value1", "value2", "value3"]
    }
    
    print(f"[DEBUG_LOG] Sending POST request to {url}")
    print(f"[DEBUG_LOG] Request data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"[DEBUG_LOG] Response status code: {response.status_code}")
        print(f"[DEBUG_LOG] Response headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"[DEBUG_LOG] Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"[DEBUG_LOG] Response text: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"[DEBUG_LOG] Connection error: {e}")
        print("[DEBUG_LOG] Make sure the Flask server is running on http://127.0.0.1:5000")
    except requests.exceptions.Timeout as e:
        print(f"[DEBUG_LOG] Timeout error: {e}")
    except Exception as e:
        print(f"[DEBUG_LOG] Unexpected error: {e}")

if __name__ == "__main__":
    test_post_kv()