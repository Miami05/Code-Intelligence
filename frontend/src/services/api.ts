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

export const searchAPI = {
  search: async (query: string) => {
    const response = await apiInstance.get("/api/search", {
      params: { q: query },
    });
    return response.data;
  },

  semanticSearch: async (query: string, repositoryId?: string) => {
    const response = await apiInstance.post("/api/search/semantic", {
      query,
      repository_id: repositoryId,
    });
    return response.data;
  },
};

export const api = apiInstance;
export default apiInstance;
