import axios from "axios";

const apiInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

apiInstance.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

apiInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      console.error("Unauthorized access");
    }
    return Promise.reject(error);
  },
);

interface SemanticSearchOptions {
  query: string;
  repository_id?: string;
  threshold?: number;
  language?: string;
  limit?: number;
}

export const searchAPI = {
  search: async (query: string) => {
    const response = await apiInstance.get("/api/search", {
      params: { q: query },
    });
    return response.data;
  },

  semanticSearch: async (options: SemanticSearchOptions | string, repoId?: string) => {
    // Handle both old signature (string, string) and new signature (object)
    let params: any = {};
    
    if (typeof options === 'string') {
      params.query = options;
      if (repoId) params.repository_id = repoId;
    } else {
      params = { ...options };
    }

    // Backend expects query parameters, not JSON body for this endpoint
    const response = await apiInstance.post("/api/search/semantic", null, {
      params: params,
    });
    return response.data;
  },
};

export const api = apiInstance;
export default apiInstance;
