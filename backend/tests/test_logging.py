import time
import os
import json
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app

# Log file paths
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = os.path.join(BASE_DIR, 'logs')
API_LOG_FILE = os.path.join(LOG_DIR, 'api.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'error.log')

def test_api_logging():
    """Test API logging by making requests to different endpoints using Flask test client"""
    print("Testing API logging...")

    # Create a test client
    client = app.test_client()

    # Test GET request
    print("Testing GET request...")
    response = client.get('/api/v1/kv')
    print(f"GET /api/v1/kv - Status: {response.status_code}")

    # Test POST request
    print("Testing POST request...")
    data = {
        "key": f"test_key_{int(time.time())}",
        "vals": ["test_value_1", "test_value_2"]
    }
    response = client.post('/api/v1/kv', json=data)
    print(f"POST /api/v1/kv - Status: {response.status_code}")

    if response.status_code == 200:
        response_data = json.loads(response.data.decode('utf-8'))
        key_id = response_data['data']['id']

        # Test PUT request
        print("Testing PUT request...")
        update_data = {
            "key": f"updated_key_{int(time.time())}",
            "vals": ["updated_value_1", "updated_value_2"]
        }
        response = client.put(f'/api/v1/kv/{key_id}', json=update_data)
        print(f"PUT /api/v1/kv/{key_id} - Status: {response.status_code}")

        # Test DELETE request
        print("Testing DELETE request...")
        response = client.delete(f'/api/v1/kv/{key_id}')
        print(f"DELETE /api/v1/kv/{key_id} - Status: {response.status_code}")

    # Test error case
    print("Testing error case...")
    response = client.get('/api/v1/kv/999999')
    print(f"GET /api/v1/kv/999999 - Status: {response.status_code}")

    # Check if log files exist
    print("\nChecking log files...")
    if os.path.exists(API_LOG_FILE):
        print(f"API log file exists: {API_LOG_FILE}")
        print(f"File size: {os.path.getsize(API_LOG_FILE)} bytes")
    else:
        print(f"API log file does not exist: {API_LOG_FILE}")

    if os.path.exists(ERROR_LOG_FILE):
        print(f"Error log file exists: {ERROR_LOG_FILE}")
        print(f"File size: {os.path.getsize(ERROR_LOG_FILE)} bytes")
    else:
        print(f"Error log file does not exist: {ERROR_LOG_FILE}")

    # Display last few lines of log files
    print("\nLast 5 lines of API log file:")
    if os.path.exists(API_LOG_FILE):
        with open(API_LOG_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(line.strip())

    print("\nLast 5 lines of Error log file:")
    if os.path.exists(ERROR_LOG_FILE):
        with open(ERROR_LOG_FILE, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(line.strip())

if __name__ == "__main__":
    # Run the test
    test_api_logging()
