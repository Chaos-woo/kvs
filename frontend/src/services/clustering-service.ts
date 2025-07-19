/**
 * K值聚类服务
 * 提供与后端聚类API的通信功能
 */

export interface ClusterNode {
  id: string;
  keys: string[];
  pattern?: string;
  similarity_score: number;
  size: number;
  children: ClusterNode[];
}

export interface ClusteringResult {
  clusters: ClusterNode[];
  total_keys: number;
  total_clusters: number;
  algorithm: string;
  parameters: {
    similarity_threshold?: number;
    min_cluster_size?: number;
  };
}

export interface ClusteringParams {
  algorithm?: 'hybrid' | 'similarity' | 'pattern';
  similarity_threshold?: number;
  min_cluster_size?: number;
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
}

/**
 * 调用后端聚类API
 */
export async function clusterKeys(params: ClusteringParams = {}): Promise<ClusteringResult> {
  const {
    algorithm = 'hybrid',
    similarity_threshold = 0.6,
    min_cluster_size = 2
  } = params;

  const queryParams = new URLSearchParams({
    algorithm,
    similarity_threshold: similarity_threshold.toString(),
    min_cluster_size: min_cluster_size.toString()
  });

  const response = await fetch(`http://127.0.0.1:5000/api/v1/kv/cluster?${queryParams}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const result: ApiResponse<ClusteringResult> = await response.json();

  if (result.status === 'error') {
    throw new Error(result.message || 'Clustering failed');
  }

  if (!result.data) {
    throw new Error('No data returned from clustering API');
  }

  return result.data;
}

/**
 * 获取聚类统计信息
 */
export function getClusteringStats(result: ClusteringResult) {
  const stats = {
    totalKeys: result.total_keys,
    totalClusters: result.total_clusters,
    algorithm: result.algorithm,
    parameters: result.parameters,
    clusterSizes: result.clusters.map(cluster => cluster.size),
    averageClusterSize: result.total_keys > 0 ? result.total_keys / result.total_clusters : 0,
    largestCluster: Math.max(...result.clusters.map(cluster => cluster.size), 0),
    smallestCluster: Math.min(...result.clusters.map(cluster => cluster.size), 0),
    singletonClusters: result.clusters.filter(cluster => cluster.size === 1).length,
    patternDistribution: getPatternDistribution(result.clusters)
  };

  return stats;
}

/**
 * 获取模式分布统计
 */
function getPatternDistribution(clusters: ClusterNode[]) {
  const patternCounts: Record<string, number> = {};
  
  clusters.forEach(cluster => {
    if (cluster.pattern) {
      const patternType = cluster.pattern.split(':')[0];
      patternCounts[patternType] = (patternCounts[patternType] || 0) + 1;
    } else {
      patternCounts['unknown'] = (patternCounts['unknown'] || 0) + 1;
    }
  });

  return patternCounts;
}

/**
 * 搜索聚类中的键
 */
export function searchClusters(clusters: ClusterNode[], query: string): ClusterNode[] {
  if (!query.trim()) {
    return clusters;
  }

  const searchTerm = query.toLowerCase();
  
  return clusters.filter(cluster => {
    // 搜索键名
    const hasMatchingKey = cluster.keys.some(key => 
      key.toLowerCase().includes(searchTerm)
    );
    
    // 搜索模式
    const hasMatchingPattern = cluster.pattern && 
      cluster.pattern.toLowerCase().includes(searchTerm);
    
    return hasMatchingKey || hasMatchingPattern;
  });
}

/**
 * 按大小排序聚类
 */
export function sortClustersBySize(clusters: ClusterNode[], ascending: boolean = false): ClusterNode[] {
  return [...clusters].sort((a, b) => {
    return ascending ? a.size - b.size : b.size - a.size;
  });
}

/**
 * 按相似度排序聚类
 */
export function sortClustersBySimilarity(clusters: ClusterNode[], ascending: boolean = false): ClusterNode[] {
  return [...clusters].sort((a, b) => {
    return ascending ? a.similarity_score - b.similarity_score : b.similarity_score - a.similarity_score;
  });
}

/**
 * 过滤聚类
 */
export function filterClusters(
  clusters: ClusterNode[], 
  filters: {
    minSize?: number;
    maxSize?: number;
    minSimilarity?: number;
    maxSimilarity?: number;
    patterns?: string[];
  }
): ClusterNode[] {
  return clusters.filter(cluster => {
    // 大小过滤
    if (filters.minSize !== undefined && cluster.size < filters.minSize) {
      return false;
    }
    if (filters.maxSize !== undefined && cluster.size > filters.maxSize) {
      return false;
    }
    
    // 相似度过滤
    if (filters.minSimilarity !== undefined && cluster.similarity_score < filters.minSimilarity) {
      return false;
    }
    if (filters.maxSimilarity !== undefined && cluster.similarity_score > filters.maxSimilarity) {
      return false;
    }
    
    // 模式过滤
    if (filters.patterns && filters.patterns.length > 0 && cluster.pattern) {
      const patternType = cluster.pattern.split(':')[0];
      if (!filters.patterns.includes(patternType)) {
        return false;
      }
    }
    
    return true;
  });
}

/**
 * 导出聚类结果为JSON
 */
export function exportClusteringResult(result: ClusteringResult): string {
  return JSON.stringify(result, null, 2);
}

/**
 * 导出聚类结果为CSV
 */
export function exportClusteringResultAsCSV(result: ClusteringResult): string {
  const headers = ['Cluster ID', 'Pattern', 'Size', 'Similarity Score', 'Keys'];
  const rows = result.clusters.map(cluster => [
    cluster.id,
    cluster.pattern || '',
    cluster.size.toString(),
    cluster.similarity_score.toFixed(3),
    cluster.keys.join('; ')
  ]);
  
  const csvContent = [headers, ...rows]
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n');
  
  return csvContent;
}