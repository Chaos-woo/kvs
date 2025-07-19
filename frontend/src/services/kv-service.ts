import { fetchFromApi } from "../utils/api";

// Interface for KV statistics API response
export interface KVStatsData {
  unique_k_count: number;
  total_v_count: number;
  v_distribution: {
    '1': number;
    '2': number;
    '3': number;
    '4': number;
    '5': number;
    '5+': number;
  };
}

export interface KVStatsResponse {
  status: string;
  data: KVStatsData;
  message?: string;
}

/**
 * Get KV statistics from the API
 * @returns Promise with KV statistics data
 */
export async function getKVStats(): Promise<KVStatsData> {
  try {
    const response = await fetchFromApi("/kv/stats");
    return response.data;
  } catch (error) {
    console.error("Error fetching KV statistics:", error);
    throw error;
  }
}