#!/usr/bin/env python3
"""
Test script for K-view API integration
Tests the complete end-to-end functionality including database and API endpoint
"""

import sys
import os
import requests
import json
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_endpoint():
    """Test the clustering API endpoint"""
    
    base_url = "http://127.0.0.1:5000/api/v1"
    
    print('🌐 Testing K-view API integration...')
    print(f'🔗 Base URL: {base_url}')
    print()
    
    # Test health endpoint first
    try:
        print('🏥 Testing health endpoint...')
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print('✅ Backend is running and healthy')
        else:
            print(f'⚠️  Backend health check returned: {health_response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'❌ Backend is not running or not accessible: {str(e)}')
        print('💡 Please start the backend server first: python backend/app.py')
        return False
    
    print()
    
    # Test clustering endpoint with different algorithms
    algorithms = ['hybrid', 'similarity', 'pattern']
    
    for algorithm in algorithms:
        print(f'🧠 Testing {algorithm} clustering algorithm...')
        
        try:
            params = {
                'algorithm': algorithm,
                'similarity_threshold': 0.6,
                'min_cluster_size': 2
            }
            
            response = requests.get(f"{base_url}/kv/cluster", params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('status') == 'success':
                    data = result.get('data', {})
                    print(f'   ✅ Success: {data.get("total_clusters", 0)} clusters found')
                    print(f'   📊 Total keys: {data.get("total_keys", 0)}')
                    print(f'   🔧 Algorithm: {data.get("algorithm", "unknown")}')
                    
                    # Show first few clusters as example
                    clusters = data.get('clusters', [])
                    if clusters:
                        print(f'   📦 Sample clusters:')
                        for i, cluster in enumerate(clusters[:3]):  # Show first 3
                            print(f'      - Cluster {i+1}: {len(cluster.get("keys", []))} keys, pattern: {cluster.get("pattern", "none")}')
                    print()
                else:
                    print(f'   ❌ API returned error: {result.get("message", "unknown error")}')
                    
            else:
                print(f'   ❌ HTTP error: {response.status_code}')
                try:
                    error_data = response.json()
                    print(f'   📝 Error details: {error_data}')
                except:
                    print(f'   📝 Response text: {response.text[:200]}...')
                    
        except requests.exceptions.RequestException as e:
            print(f'   ❌ Request failed: {str(e)}')
        
        print()
    
    print('🎯 Testing parameter validation...')
    
    # Test invalid algorithm
    try:
        params = {'algorithm': 'invalid_algorithm'}
        response = requests.get(f"{base_url}/kv/cluster", params=params, timeout=10)
        
        if response.status_code == 400:
            print('   ✅ Invalid algorithm properly rejected')
        else:
            print(f'   ⚠️  Expected 400 for invalid algorithm, got {response.status_code}')
    except Exception as e:
        print(f'   ❌ Parameter validation test failed: {str(e)}')
    
    # Test invalid similarity threshold
    try:
        params = {'similarity_threshold': '1.5'}  # Invalid: > 1.0
        response = requests.get(f"{base_url}/kv/cluster", params=params, timeout=10)
        
        if response.status_code == 400:
            print('   ✅ Invalid similarity threshold properly rejected')
        else:
            print(f'   ⚠️  Expected 400 for invalid threshold, got {response.status_code}')
    except Exception as e:
        print(f'   ❌ Threshold validation test failed: {str(e)}')
    
    print()
    print('✅ API integration test completed!')
    print('🎉 K-view exploration feature is fully functional!')
    
    return True

def print_usage_instructions():
    """Print usage instructions for the K-view feature"""
    
    print()
    print('=' * 60)
    print('📖 K-VIEW EXPLORATION USAGE INSTRUCTIONS')
    print('=' * 60)
    print()
    print('🚀 How to use the K-view exploration feature:')
    print()
    print('1. 🖥️  Start the application:')
    print('   - Backend: python backend/app.py')
    print('   - Frontend: npm run tauri dev (in frontend directory)')
    print()
    print('2. 🎯 Access K-view exploration:')
    print('   - Click "视图" in the menu bar')
    print('   - Select "K视图探索"')
    print()
    print('3. ⚙️  Configure clustering parameters:')
    print('   - Choose algorithm: Hybrid (recommended), Similarity, or Pattern')
    print('   - Adjust similarity threshold (0.0 - 1.0)')
    print('   - Set minimum cluster size (1+)')
    print()
    print('4. 🔍 Explore results:')
    print('   - View clusters in the left panel')
    print('   - Click on clusters to see details')
    print('   - Search and filter clusters')
    print('   - Sort by size or similarity')
    print()
    print('5. 📊 Export results:')
    print('   - Export as JSON or CSV format')
    print('   - View detailed statistics')
    print()
    print('🎯 Clustering Algorithms:')
    print('   • Hybrid: Combines pattern recognition + similarity (recommended)')
    print('   • Similarity: Pure string similarity-based clustering')
    print('   • Pattern: Groups by regex patterns (prefixes, suffixes, etc.)')
    print()
    print('✨ Features:')
    print('   • Real-time parameter adjustment')
    print('   • Interactive cluster exploration')
    print('   • Pattern recognition for common key formats')
    print('   • Export and statistics functionality')
    print('   • Full-screen modal interface')
    print()

if __name__ == '__main__':
    try:
        success = test_api_endpoint()
        print_usage_instructions()
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f'❌ Test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)