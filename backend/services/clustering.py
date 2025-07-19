"""
K值聚类服务模块
实现基于字符串相似度、模式识别和层次聚类的混合聚类方案
"""

import re
import difflib
from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict, Counter
import math
from dataclasses import dataclass


@dataclass
class ClusterNode:
    """聚类节点数据结构"""
    id: str
    keys: List[str]
    pattern: Optional[str] = None
    similarity_score: float = 0.0
    children: List['ClusterNode'] = None
    
    def __post_init__(self):
        if self.children is None:
            self.children = []


class StringSimilarityCalculator:
    """字符串相似度计算器"""
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """计算编辑距离"""
        if len(s1) < len(s2):
            return StringSimilarityCalculator.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def similarity_ratio(s1: str, s2: str) -> float:
        """计算相似度比率 (0-1)"""
        return difflib.SequenceMatcher(None, s1, s2).ratio()
    
    @staticmethod
    def jaccard_similarity(s1: str, s2: str, n: int = 2) -> float:
        """计算Jaccard相似度（基于n-gram）"""
        def get_ngrams(text: str, n: int) -> set:
            return set(text[i:i+n] for i in range(len(text) - n + 1))
        
        ngrams1 = get_ngrams(s1, n)
        ngrams2 = get_ngrams(s2, n)
        
        if not ngrams1 and not ngrams2:
            return 1.0
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def combined_similarity(s1: str, s2: str) -> float:
        """组合相似度计算"""
        ratio_sim = StringSimilarityCalculator.similarity_ratio(s1, s2)
        jaccard_sim = StringSimilarityCalculator.jaccard_similarity(s1, s2)
        
        # 加权组合
        return 0.7 * ratio_sim + 0.3 * jaccard_sim


class PatternRecognizer:
    """模式识别器"""
    
    # 常见模式定义
    PATTERNS = {
        'numeric_suffix': r'^(.+?)_?(\d+)$',
        'date_pattern': r'^(.+?)_?(\d{4}[-_]\d{2}[-_]\d{2})$',
        'timestamp_pattern': r'^(.+?)_?(\d{10,13})$',
        'uuid_pattern': r'^(.+?)_?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        'version_pattern': r'^(.+?)_?v?(\d+\.\d+(?:\.\d+)?)$',
        'prefix_pattern': r'^([a-zA-Z]+)_(.+)$',
        'camel_case': r'^([a-z]+)([A-Z][a-zA-Z0-9]*)$',
    }
    
    @classmethod
    def extract_pattern(cls, key: str) -> Tuple[str, str]:
        """提取键的模式"""
        key_lower = key.lower()
        
        for pattern_name, pattern_regex in cls.PATTERNS.items():
            match = re.match(pattern_regex, key, re.IGNORECASE)
            if match:
                return pattern_name, match.group(1) if match.group(1) else key
        
        # 如果没有匹配到特定模式，尝试提取公共前缀
        return 'literal', key
    
    @classmethod
    def group_by_patterns(cls, keys: List[str]) -> Dict[str, List[str]]:
        """按模式分组键"""
        pattern_groups = defaultdict(list)
        
        for key in keys:
            pattern_type, base_pattern = cls.extract_pattern(key)
            pattern_groups[f"{pattern_type}:{base_pattern}"].append(key)
        
        return dict(pattern_groups)
    
    @classmethod
    def find_common_prefix(cls, keys: List[str]) -> str:
        """找到键列表的公共前缀"""
        if not keys:
            return ""
        
        if len(keys) == 1:
            return keys[0]
        
        # 找到最短的键作为基准
        min_key = min(keys, key=len)
        
        for i, char in enumerate(min_key):
            if not all(key[i] == char for key in keys if i < len(key)):
                return min_key[:i]
        
        return min_key


class HierarchicalClusterer:
    """层次聚类器"""
    
    def __init__(self, similarity_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold
        self.similarity_calc = StringSimilarityCalculator()
    
    def cluster_keys(self, keys: List[str]) -> List[ClusterNode]:
        """对键进行层次聚类"""
        if not keys:
            return []
        
        if len(keys) == 1:
            return [ClusterNode(id="cluster_0", keys=keys)]
        
        # 计算相似度矩阵
        similarity_matrix = self._compute_similarity_matrix(keys)
        
        # 执行层次聚类
        clusters = self._hierarchical_clustering(keys, similarity_matrix)
        
        return clusters
    
    def _compute_similarity_matrix(self, keys: List[str]) -> List[List[float]]:
        """计算相似度矩阵"""
        n = len(keys)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self.similarity_calc.combined_similarity(keys[i], keys[j])
                matrix[i][j] = similarity
                matrix[j][i] = similarity
            matrix[i][i] = 1.0
        
        return matrix
    
    def _hierarchical_clustering(self, keys: List[str], similarity_matrix: List[List[float]]) -> List[ClusterNode]:
        """执行层次聚类"""
        # 初始化每个键为一个簇
        clusters = [ClusterNode(id=f"cluster_{i}", keys=[key]) for i, key in enumerate(keys)]
        cluster_indices = list(range(len(keys)))
        
        while len(clusters) > 1:
            # 找到最相似的两个簇
            max_similarity = -1
            merge_i, merge_j = -1, -1
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    # 计算簇间相似度（使用平均链接）
                    cluster_similarity = self._compute_cluster_similarity(
                        clusters[i], clusters[j], keys, similarity_matrix
                    )
                    
                    if cluster_similarity > max_similarity:
                        max_similarity = cluster_similarity
                        merge_i, merge_j = i, j
            
            # 如果最大相似度低于阈值，停止合并
            if max_similarity < self.similarity_threshold:
                break
            
            # 合并两个最相似的簇
            merged_cluster = ClusterNode(
                id=f"merged_{merge_i}_{merge_j}",
                keys=clusters[merge_i].keys + clusters[merge_j].keys,
                similarity_score=max_similarity,
                children=[clusters[merge_i], clusters[merge_j]]
            )
            
            # 移除被合并的簇，添加新簇
            new_clusters = []
            for k, cluster in enumerate(clusters):
                if k != merge_i and k != merge_j:
                    new_clusters.append(cluster)
            new_clusters.append(merged_cluster)
            clusters = new_clusters
        
        return clusters
    
    def _compute_cluster_similarity(self, cluster1: ClusterNode, cluster2: ClusterNode, 
                                  keys: List[str], similarity_matrix: List[List[float]]) -> float:
        """计算两个簇之间的相似度（平均链接）"""
        similarities = []
        
        for key1 in cluster1.keys:
            for key2 in cluster2.keys:
                i = keys.index(key1)
                j = keys.index(key2)
                similarities.append(similarity_matrix[i][j])
        
        return sum(similarities) / len(similarities) if similarities else 0.0


class KValueClusteringService:
    """K值聚类服务主类"""
    
    def __init__(self, similarity_threshold: float = 0.6, min_cluster_size: int = 2):
        self.similarity_threshold = similarity_threshold
        self.min_cluster_size = min_cluster_size
        self.pattern_recognizer = PatternRecognizer()
        self.hierarchical_clusterer = HierarchicalClusterer(similarity_threshold)
    
    def cluster_keys(self, keys: List[str], algorithm: str = "hybrid") -> Dict[str, Any]:
        """
        对键进行聚类
        
        Args:
            keys: 要聚类的键列表
            algorithm: 聚类算法 ("hybrid", "similarity", "pattern")
        
        Returns:
            聚类结果字典
        """
        if not keys:
            return {"clusters": [], "total_keys": 0, "total_clusters": 0}
        
        if algorithm == "hybrid":
            return self._hybrid_clustering(keys)
        elif algorithm == "similarity":
            return self._similarity_clustering(keys)
        elif algorithm == "pattern":
            return self._pattern_clustering(keys)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def _hybrid_clustering(self, keys: List[str]) -> Dict[str, Any]:
        """混合聚类方法"""
        # 第一层：基于模式的粗分类
        pattern_groups = self.pattern_recognizer.group_by_patterns(keys)
        
        final_clusters = []
        cluster_id = 0
        
        for pattern_key, pattern_keys in pattern_groups.items():
            if len(pattern_keys) < self.min_cluster_size:
                # 小组直接作为一个簇
                final_clusters.append(ClusterNode(
                    id=f"cluster_{cluster_id}",
                    keys=pattern_keys,
                    pattern=pattern_key
                ))
                cluster_id += 1
            else:
                # 第二层：在模式组内使用相似度聚类
                sub_clusters = self.hierarchical_clusterer.cluster_keys(pattern_keys)
                
                for sub_cluster in sub_clusters:
                    sub_cluster.id = f"cluster_{cluster_id}"
                    sub_cluster.pattern = pattern_key
                    final_clusters.append(sub_cluster)
                    cluster_id += 1
        
        return {
            "clusters": [self._cluster_to_dict(cluster) for cluster in final_clusters],
            "total_keys": len(keys),
            "total_clusters": len(final_clusters),
            "algorithm": "hybrid",
            "parameters": {
                "similarity_threshold": self.similarity_threshold,
                "min_cluster_size": self.min_cluster_size
            }
        }
    
    def _similarity_clustering(self, keys: List[str]) -> Dict[str, Any]:
        """基于相似度的聚类"""
        clusters = self.hierarchical_clusterer.cluster_keys(keys)
        
        return {
            "clusters": [self._cluster_to_dict(cluster) for cluster in clusters],
            "total_keys": len(keys),
            "total_clusters": len(clusters),
            "algorithm": "similarity",
            "parameters": {
                "similarity_threshold": self.similarity_threshold
            }
        }
    
    def _pattern_clustering(self, keys: List[str]) -> Dict[str, Any]:
        """基于模式的聚类"""
        pattern_groups = self.pattern_recognizer.group_by_patterns(keys)
        
        clusters = []
        for i, (pattern_key, pattern_keys) in enumerate(pattern_groups.items()):
            clusters.append(ClusterNode(
                id=f"cluster_{i}",
                keys=pattern_keys,
                pattern=pattern_key
            ))
        
        return {
            "clusters": [self._cluster_to_dict(cluster) for cluster in clusters],
            "total_keys": len(keys),
            "total_clusters": len(clusters),
            "algorithm": "pattern",
            "parameters": {}
        }
    
    def _cluster_to_dict(self, cluster: ClusterNode) -> Dict[str, Any]:
        """将聚类节点转换为字典"""
        return {
            "id": cluster.id,
            "keys": cluster.keys,
            "pattern": cluster.pattern,
            "similarity_score": cluster.similarity_score,
            "size": len(cluster.keys),
            "children": [self._cluster_to_dict(child) for child in cluster.children] if cluster.children else []
        }