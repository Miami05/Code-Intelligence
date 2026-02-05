import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api";

export interface SearchResult {
  symbol_id: string;
  name: string;
  type: string;
  signature: string;
  file_path: string;
  repository_id: string;
  similarity: number;
  lines?: string;
}

export interface SearchResponse {
  query: string;
  threshold: number;
  total_results: number;
  results: SearchResult[];
}

export const searchAPI = {
  semanticSearch: async (
    query: string,
    threshold: number = 0.4,
  ): Promise<SearchResponse> => {
    const response = await axios.post<SearchResponse>(
      `${API_BASE_URL}/search/semantic`,
      null,
      {
        params: { query, threshold },
      },
    );
    return response.data;
  },
};
