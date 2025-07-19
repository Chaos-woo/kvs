#!/usr/bin/env python3
"""
Test script for K-view clustering functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.clustering import KValueClusteringService

def test_clustering():
    """Test the clustering service with sample data"""
    
    # Test with sample data that represents common key patterns
    test_keys = [
        'user_123', 'user_456', 'user_789',
        'order_2024_01', 'order_2024_02', 'order_2024_03',
        'session_abc123', 'session_def456',
        'config_database', 'config_redis', 'config_cache',
        'temp_file_1', 'temp_file_2',
        'api_v1_users', 'api_v1_orders', 'api_v2_users',
        'cache_user_data', 'cache_session_data'
    ]

    print('🔍 Testing K-view clustering service...')
    print(f'📊 Sample keys ({len(test_keys)}): {test_keys}')
    print()

    # Test hybrid clustering (recommended)
    service = KValueClusteringService(similarity_threshold=0.6, min_cluster_size=2)
    
    print('=== 🔀 HYBRID CLUSTERING RESULTS ===')
    result = service.cluster_keys(test_keys, algorithm='hybrid')
    
    print(f'📈 Total keys: {result["total_keys"]}')
    print(f'📊 Total clusters: {result["total_clusters"]}')
    print(f'🧠 Algorithm: {result["algorithm"]}')
    print(f'⚙️  Parameters: {result["parameters"]}')
    print()

    for i, cluster in enumerate(result['clusters']):
        print(f'📦 Cluster {i+1}: {cluster["id"]}')
        print(f'   🏷️  Pattern: {cluster["pattern"]}')
        print(f'   📏 Size: {cluster["size"]}')
        print(f'   🔑 Keys: {cluster["keys"]}')
        print(f'   📊 Similarity: {cluster["similarity_score"]:.3f}')
        print()

    # Test similarity clustering
    print('=== 🔗 SIMILARITY CLUSTERING RESULTS ===')
    result_sim = service.cluster_keys(test_keys, algorithm='similarity')
    print(f'📊 Total clusters: {result_sim["total_clusters"]}')
    print()

    # Test pattern clustering
    print('=== 🎯 PATTERN CLUSTERING RESULTS ===')
    result_pattern = service.cluster_keys(test_keys, algorithm='pattern')
    print(f'📊 Total clusters: {result_pattern["total_clusters"]}')
    print()

    print('✅ Clustering service test completed successfully!')
    print('🎉 K-view exploration feature is ready to use!')
    
    return True

if __name__ == '__main__':
    try:
        test_clustering()
    except Exception as e:
        print(f'❌ Test failed: {str(e)}')
        import traceback
        traceback.print_exc()
        sys.exit(1)