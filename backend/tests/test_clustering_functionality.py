#!/usr/bin/env python3
"""
测试K值聚类功能
验证后端聚类服务和API端点的功能
"""

import sys
import os
import requests
import json
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

def test_clustering_service():
    """测试聚类服务模块"""
    print("=" * 50)
    print("测试聚类服务模块")
    print("=" * 50)
    
    try:
        from services.clustering import KValueClusteringService
        
        # 创建测试数据
        test_keys = [
            "user_123", "user_456", "user_789",
            "order_2024_01", "order_2024_02", "order_2024_03",
            "session_abc123", "session_def456", "session_ghi789",
            "config_database", "config_redis", "config_cache",
            "temp_file_1", "temp_file_2",
            "log_2024-01-01", "log_2024-01-02",
            "api_key_v1", "api_key_v2",
            "single_key"
        ]
        
        print(f"测试数据: {len(test_keys)} 个键")
        for key in test_keys:
            print(f"  - {key}")
        
        # 创建聚类服务实例
        clustering_service = KValueClusteringService(
            similarity_threshold=0.6,
            min_cluster_size=2
        )
        
        # 测试混合聚类
        print("\n测试混合聚类算法...")
        result = clustering_service.cluster_keys(test_keys, algorithm="hybrid")
        print(f"聚类结果: {result['total_clusters']} 个聚类，包含 {result['total_keys']} 个键")
        
        for i, cluster in enumerate(result['clusters']):
            print(f"  聚类 {i+1}: {cluster['size']} 个键")
            print(f"    模式: {cluster.get('pattern', 'N/A')}")
            print(f"    键: {cluster['keys']}")
        
        # 测试相似度聚类
        print("\n测试相似度聚类算法...")
        result = clustering_service.cluster_keys(test_keys, algorithm="similarity")
        print(f"聚类结果: {result['total_clusters']} 个聚类，包含 {result['total_keys']} 个键")
        
        # 测试模式聚类
        print("\n测试模式聚类算法...")
        result = clustering_service.cluster_keys(test_keys, algorithm="pattern")
        print(f"聚类结果: {result['total_clusters']} 个聚类，包含 {result['total_keys']} 个键")
        
        print("\n✅ 聚类服务模块测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 聚类服务模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_clustering_api():
    """测试聚类API端点"""
    print("\n" + "=" * 50)
    print("测试聚类API端点")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000/api/v1"
    
    try:
        # 测试健康检查
        print("测试后端连接...")
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ 后端服务连接正常")
        else:
            print("❌ 后端服务连接失败")
            return False
        
        # 测试聚类API
        print("\n测试聚类API...")
        
        # 测试不同的参数组合
        test_params = [
            {"algorithm": "hybrid", "similarity_threshold": 0.6, "min_cluster_size": 2},
            {"algorithm": "similarity", "similarity_threshold": 0.7, "min_cluster_size": 1},
            {"algorithm": "pattern", "min_cluster_size": 1},
        ]
        
        for params in test_params:
            print(f"\n测试参数: {params}")
            response = requests.get(f"{base_url}/kv/cluster", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    result = data.get("data", {})
                    print(f"✅ 聚类成功: {result.get('total_clusters', 0)} 个聚类，"
                          f"{result.get('total_keys', 0)} 个键")
                    print(f"   算法: {result.get('algorithm', 'N/A')}")
                else:
                    print(f"❌ 聚类失败: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ API请求失败: HTTP {response.status_code}")
                print(f"   响应: {response.text}")
        
        print("\n✅ 聚类API测试完成")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保Flask服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 聚类API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """测试边缘情况"""
    print("\n" + "=" * 50)
    print("测试边缘情况")
    print("=" * 50)
    
    try:
        from services.clustering import KValueClusteringService
        
        clustering_service = KValueClusteringService()
        
        # 测试空列表
        print("测试空键列表...")
        result = clustering_service.cluster_keys([])
        assert result['total_keys'] == 0
        assert result['total_clusters'] == 0
        print("✅ 空列表测试通过")
        
        # 测试单个键
        print("测试单个键...")
        result = clustering_service.cluster_keys(["single_key"])
        assert result['total_keys'] == 1
        print("✅ 单个键测试通过")
        
        # 测试相同的键
        print("测试相同的键...")
        result = clustering_service.cluster_keys(["same_key", "same_key", "same_key"])
        print(f"相同键聚类结果: {result['total_clusters']} 个聚类")
        
        # 测试特殊字符
        print("测试特殊字符...")
        special_keys = ["key@#$%", "key!@#", "key_with_spaces ", "key\twith\ttabs"]
        result = clustering_service.cluster_keys(special_keys)
        print(f"特殊字符聚类结果: {result['total_clusters']} 个聚类")
        
        print("\n✅ 边缘情况测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 边缘情况测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试K值聚类功能")
    print("时间:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 运行所有测试
    tests = [
        ("聚类服务模块", test_clustering_service),
        ("边缘情况", test_edge_cases),
        ("聚类API端点", test_clustering_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {e}")
            results.append((test_name, False))
    
    # 输出测试总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！K值聚类功能实现正确。")
        return True
    else:
        print("⚠️  部分测试失败，请检查实现。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)