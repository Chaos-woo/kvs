import { invoke } from "@tauri-apps/api/tauri";
import { logger } from "./logger";

const API_BASE_URL = "http://127.0.0.1:5000/api/v1";

// Flag to track if we've already shown the backend connection error
let backendErrorShown = false;

export async function fetchFromApi(endpoint: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const method = options.method || 'GET';
  const TIMEOUT_MS = 2000; // 2 seconds timeout

  try {
    // Log the request
    logger.info(`API Request: ${method} ${url}`);
    if (options.body) {
      logger.debug(`Request Body: ${options.body}`);
    }

    const startTime = performance.now();

    // Create a promise that rejects after the timeout
    const timeoutPromise = new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timeout')), TIMEOUT_MS);
    });

    // Race the fetch against the timeout
    const response = await Promise.race([
      fetch(url, {
        ...options,
        headers: {
          ...(options.body ? { "Content-Type": "application/json" } : {}),
          ...options.headers,
        },
      }),
      timeoutPromise
    ]) as Response;

    const endTime = performance.now();
    const duration = Math.round(endTime - startTime);

    if (!response.ok) {
      const errorMessage = `API error: ${response.status} ${response.statusText}`;
      logger.error(`${errorMessage} (${duration}ms) - ${method} ${url}`);
      throw new Error(errorMessage);
    }

    const data = await response.json();

    // Log the response
    logger.info(`API Response: ${response.status} (${duration}ms) - ${method} ${url}`);
    logger.debug(`Response Data: ${JSON.stringify(data)}`);

    // Reset the error flag since we successfully connected to the backend
    backendErrorShown = false;

    return data;
  } catch (error) {
    logger.error(`API request failed: ${method} ${url}`, error);

    // If this is the first backend error, log a more detailed message
    if (!backendErrorShown) {
      console.error(`
        Backend connection error: Unable to connect to the backend server at ${API_BASE_URL}.
        Please make sure the backend server is running by using the command:
        npm run dev-with-backend

        For now, the application will continue with limited functionality.
      `);
      backendErrorShown = true;
    }

    // Return mock data based on the endpoint to prevent UI from breaking
    return getMockData(endpoint, method, options);
  }
}

// Function to provide mock data when the backend is not available
function getMockData(endpoint: string, method: string, options: RequestInit) {
  // Default success response
  const successResponse = {
    status: "success",
    message: "Operation completed successfully (mock data)",
  };

  // Mock data for different endpoints
  if (endpoint === "/theme") {
    return { ...successResponse, theme: "light" };
  }

  if (endpoint === "/health") {
    return { ...successResponse, status: "ok" };
  }

  if (endpoint === "/kv" && method === "GET") {
    return { 
      ...successResponse, 
      data: [] // Empty array for KV data
    };
  }

  if (endpoint.includes("/kv/search")) {
    return { 
      ...successResponse, 
      data: [] // Empty search results
    };
  }

  if (endpoint === "/kv" && method === "POST") {
    return { 
      ...successResponse, 
      data: { 
        id: Math.floor(Math.random() * 1000),
        key: JSON.parse(options.body as string).key,
        vals: JSON.parse(options.body as string).vals,
        created_at: new Date().toISOString(),
        updated_at: null
      }
    };
  }

  // Default fallback for any other endpoints
  return successResponse;
}

export async function getTab1Data() {
  return fetchFromApi("/tab1");
}

export async function getTab2Data() {
  return fetchFromApi("/tab2");
}

// KV API functions

export interface KVData {
  id: number;
  key: string;
  vals: string[];
  created_at: string;
  updated_at: string | null;
}

export async function createKV(key: string, vals: string[]) {
  return fetchFromApi("/kv", {
    method: "POST",
    body: JSON.stringify({ key, vals }),
  });
}

export async function updateKV(keyId: number, key: string, vals: string[]) {
  return fetchFromApi(`/kv/${keyId}`, {
    method: "PUT",
    body: JSON.stringify({ key, vals }),
  });
}

export async function deleteKV(keyId: number) {
  return fetchFromApi(`/kv/${keyId}`, {
    method: "DELETE",
  });
}

export async function searchKV(query: string, mode: string = 'mixed') {
  return fetchFromApi(`/kv/search?q=${encodeURIComponent(query)}&mode=${encodeURIComponent(mode)}`);
}

export async function getAllKVs() {
  return fetchFromApi("/kv");
}

export async function getKV(keyId: number) {
  return fetchFromApi(`/kv/${keyId}`);
}
