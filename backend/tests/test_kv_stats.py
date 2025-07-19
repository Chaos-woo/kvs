import requests
import json

def test_kv_stats_endpoint():
    """Test the KV statistics endpoint"""
    try:
        # Test the KV stats endpoint
        response = requests.get("http://127.0.0.1:5000/api/v1/kv/stats")
        
        print(f"[DEBUG_LOG] Response status code: {response.status_code}")
        print(f"[DEBUG_LOG] Response headers: {response.headers}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[DEBUG_LOG] Response data: {json.dumps(data, indent=2)}")
            
            # Validate response structure
            if data.get("status") == "success" and "data" in data:
                stats_data = data["data"]
                required_fields = ["unique_k_count", "total_v_count", "v_distribution"]
                
                for field in required_fields:
                    if field not in stats_data:
                        print(f"[DEBUG_LOG] ERROR: Missing field '{field}' in response")
                        return False
                
                # Validate v_distribution structure
                v_dist = stats_data["v_distribution"]
                expected_keys = ['1', '2', '3', '4', '5', '5+']
                for key in expected_keys:
                    if key not in v_dist:
                        print(f"[DEBUG_LOG] ERROR: Missing key '{key}' in v_distribution")
                        return False
                
                print("[DEBUG_LOG] SUCCESS: KV stats endpoint working correctly!")
                return True
            else:
                print(f"[DEBUG_LOG] ERROR: Invalid response structure")
                return False
        else:
            print(f"[DEBUG_LOG] ERROR: HTTP {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[DEBUG_LOG] ERROR: Cannot connect to backend server. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"[DEBUG_LOG] ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("[DEBUG_LOG] Testing KV Statistics API endpoint...")
    success = test_kv_stats_endpoint()
    if success:
        print("[DEBUG_LOG] Test PASSED!")
    else:
        print("[DEBUG_LOG] Test FAILED!")